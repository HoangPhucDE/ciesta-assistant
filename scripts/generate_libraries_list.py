#!/usr/bin/env python3
"""
Script để tự động liệt kê tất cả thư viện được sử dụng trong dự án
"""

import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, Set, List

def extract_imports_from_file(file_path: Path) -> Set[str]:
    """Extract all imports from a Python file"""
    imports = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Match import statements
        # Pattern 1: import module
        pattern1 = r'^import\s+([a-zA-Z0-9_]+)'
        matches1 = re.findall(pattern1, content, re.MULTILINE)
        imports.update(matches1)
        
        # Pattern 2: from module import ...
        pattern2 = r'^from\s+([a-zA-Z0-9_.]+)\s+import'
        matches2 = re.findall(pattern2, content, re.MULTILINE)
        # Extract root module name
        for match in matches2:
            root_module = match.split('.')[0]
            imports.add(root_module)
            
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return imports

def read_requirements() -> Dict[str, str]:
    """Read requirements.txt and return package names and versions"""
    requirements = {}
    req_file = Path("requirements.txt")
    
    if req_file.exists():
        with open(req_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Parse package==version
                    if '==' in line:
                        parts = line.split('==')
                        if len(parts) == 2:
                            requirements[parts[0].strip()] = parts[1].strip()
                    elif '>=' in line:
                        parts = line.split('>=')
                        if len(parts) == 2:
                            requirements[parts[0].strip()] = f">={parts[1].strip()}"
                    elif line:
                        requirements[line.strip()] = "unknown"
    
    return requirements

def scan_project() -> Dict[str, List[str]]:
    """Scan project for all Python files and extract imports"""
    project_root = Path(".")
    
    # Directories to scan
    scan_dirs = [
        "custom_components",
        "actions",
        "rag",
        "ciesta",
        "scripts",
        "utils",
    ]
    
    # Files to scan
    scan_files = [
        "test_phobert_local.py",
        "reorganize.py",
    ]
    
    all_imports = defaultdict(list)
    
    # Scan directories
    for dir_name in scan_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            for py_file in dir_path.rglob("*.py"):
                imports = extract_imports_from_file(py_file)
                for imp in imports:
                    all_imports[imp].append(str(py_file.relative_to(project_root)))
    
    # Scan individual files
    for file_name in scan_files:
        file_path = project_root / file_name
        if file_path.exists():
            imports = extract_imports_from_file(file_path)
            for imp in imports:
                all_imports[imp].append(file_name)
    
    return dict(all_imports)

def filter_standard_library(imports: Set[str]) -> Set[str]:
    """Filter out Python standard library modules"""
    stdlib_modules = {
        'os', 'sys', 'json', 're', 'pathlib', 'typing', 'datetime', 'time',
        'subprocess', 'shutil', 'logging', 'collections', 'itertools',
        'functools', 'operator', 'hashlib', 'base64', 'urllib', 'http',
        'asyncio', 'threading', 'multiprocessing', 'queue', 'socket',
        'email', 'csv', 'xml', 'html', 'unicodedata', 'codecs', 'io',
        'tempfile', 'tarfile', 'zipfile', 'pickle', 'copy', 'weakref',
        'abc', 'enum', 'dataclasses', 'contextlib', 'argparse', 'getopt',
        'configparser', 'logging', 'warnings', 'traceback', 'inspect',
        'pdb', 'profile', 'pstats', 'timeit', 'doctest', 'unittest',
        'test', 'pkgutil', 'importlib', 'imp', 'modulefinder', 'pkgutil',
        'zipimport', 'pydoc', 'doctest', 'unittest', '2to3', 'lib2to3'
    }
    
    # Filter out standard library
    third_party = {imp for imp in imports if imp not in stdlib_modules}
    
    # Also filter out if it's a local module (starts with custom_, rag_, etc.)
    third_party = {imp for imp in third_party if not any(
        imp.startswith(prefix) for prefix in ['custom_', 'rag_', 'ciesta', 'actions', 'utils']
    )}
    
    return third_party

def main():
    """Main function"""
    print("=" * 60)
    print("SCANNING PROJECT FOR LIBRARIES")
    print("=" * 60)
    print()
    
    # Read requirements.txt
    print("📦 Reading requirements.txt...")
    requirements = read_requirements()
    print(f"   Found {len(requirements)} packages in requirements.txt")
    print()
    
    # Scan project
    print("🔍 Scanning Python files...")
    imports = scan_project()
    print(f"   Found {len(imports)} unique imports")
    print()
    
    # Filter standard library
    print("🔧 Filtering standard library...")
    third_party = filter_standard_library(set(imports.keys()))
    print(f"   Found {len(third_party)} third-party libraries")
    print()
    
    # Generate report
    print("=" * 60)
    print("LIBRARIES FOUND IN CODE")
    print("=" * 60)
    print()
    
    # Sort by name
    sorted_imports = sorted(third_party)
    
    # Categorize
    categories = {
        "Rasa": ["rasa"],
        "ML/NLP": ["transformers", "torch", "numpy", "faiss", "tokenizers", "sentencepiece", "huggingface"],
        "LLM APIs": ["openai", "groq", "google"],
        "GUI": ["PySide6", "PyQt6"],
        "Web": ["flask", "requests", "aiohttp"],
        "Utilities": ["dotenv", "rich", "tqdm", "pandas", "matplotlib", "seaborn", "plotly"],
        "Development": ["black", "isort", "ruff", "jupyter", "ipykernel"],
        "Other": []
    }
    
    categorized = {cat: [] for cat in categories}
    
    for imp in sorted_imports:
        categorized_flag = False
        for category, keywords in categories.items():
            if any(keyword.lower() in imp.lower() for keyword in keywords):
                categorized[category].append(imp)
                categorized_flag = True
                break
        if not categorized_flag:
            categorized["Other"].append(imp)
    
    # Print categorized
    for category, libs in categorized.items():
        if libs:
            print(f"📚 {category}:")
            for lib in sorted(libs):
                version = requirements.get(lib, "not in requirements.txt")
                files = imports.get(lib, [])
                print(f"   - {lib} ({version})")
                if files:
                    print(f"     Used in: {', '.join(files[:3])}")
                    if len(files) > 3:
                        print(f"     ... and {len(files) - 3} more files")
            print()
    
    # Print requirements.txt packages not found in code
    print("=" * 60)
    print("PACKAGES IN requirements.txt BUT NOT FOUND IN CODE")
    print("=" * 60)
    print()
    
    req_not_in_code = set(requirements.keys()) - third_party
    if req_not_in_code:
        for pkg in sorted(req_not_in_code):
            print(f"   - {pkg} ({requirements[pkg]})")
    else:
        print("   None (all packages are used)")
    print()
    
    # Print summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total packages in requirements.txt: {len(requirements)}")
    print(f"Third-party libraries found in code: {len(third_party)}")
    print(f"Packages in requirements.txt but not in code: {len(req_not_in_code)}")
    print()

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
BOF Indexer - Extract BOF names and descriptions from BOF-pack repositories.

This script:
1. Extracts repository URLs from the bofs-catalog.md
2. Clones repositories to a local directory
3. Parses various documentation formats to extract BOF metadata
4. Outputs a JSON file with BOF name, description, and source repository
"""

import os
import re
import json
import subprocess
import argparse
import sys
from pathlib import Path
from collections import defaultdict
from typing import Optional
from dataclasses import dataclass, field, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class BOFEntry:
    """Represents a single BOF command/tool."""
    name: str
    description: str
    repository: str
    source_file: str = ""
    source_format: str = ""  # e.g., "readme_table", "cna", "havoc_py", "stage1_py"


@dataclass 
class RepoInfo:
    """Repository information."""
    url: str
    owner: str
    name: str
    local_path: str = ""
    clone_success: bool = False
    bofs_found: list = field(default_factory=list)
    parse_formats_found: list = field(default_factory=list)


# =============================================================================
# URL Extraction (adapted from find-dupes.py)
# =============================================================================

MARKDOWN_LINK_PATTERN = re.compile(r'\[.*?\]\(([^)]+)\)')
GITHUB_REPO_PATTERN = re.compile(r'^https?://github\.com/([\w._-]+)/([\w._-]+)')
GITLAB_REPO_PATTERN = re.compile(r'^https?://gitlab\.com/([\w._-]+)/([\w._-]+)')


def extract_repo_urls_from_catalog(catalog_path: str) -> list[RepoInfo]:
    """Extract all repository URLs from the catalog markdown file."""
    repos = []
    seen_urls = set()
    
    with open(catalog_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            stripped_line = line.strip()
            
            # Check if the line looks like a table row
            if not stripped_line.startswith('|') or not stripped_line.endswith('|'):
                continue

            parts = stripped_line.split('|')
            if len(parts) < 4:
                continue

            first_col_content = parts[1].strip()
            link_match = MARKDOWN_LINK_PATTERN.search(first_col_content)
            if not link_match:
                continue

            url = link_match.group(1).strip()
            
            # Try GitHub first
            repo_match = GITHUB_REPO_PATTERN.match(url)
            if repo_match:
                owner = repo_match.group(1)
                name = repo_match.group(2).rstrip('./')
                normalized_url = f"https://github.com/{owner}/{name}".lower()
                
                if normalized_url not in seen_urls:
                    seen_urls.add(normalized_url)
                    repos.append(RepoInfo(
                        url=f"https://github.com/{owner}/{name}",
                        owner=owner,
                        name=name
                    ))
                continue
            
            # Try GitLab
            repo_match = GITLAB_REPO_PATTERN.match(url)
            if repo_match:
                owner = repo_match.group(1)
                name = repo_match.group(2).rstrip('./')
                normalized_url = f"https://gitlab.com/{owner}/{name}".lower()
                
                if normalized_url not in seen_urls:
                    seen_urls.add(normalized_url)
                    repos.append(RepoInfo(
                        url=f"https://gitlab.com/{owner}/{name}",
                        owner=owner,
                        name=name
                    ))
    
    return repos


# =============================================================================
# Repository Cloning
# =============================================================================

def clone_repo(repo: RepoInfo, repos_dir: str, timeout: int = 60) -> RepoInfo:
    """Clone a single repository with depth=1."""
    local_path = os.path.join(repos_dir, f"{repo.owner}__{repo.name}")
    repo.local_path = local_path
    
    if os.path.exists(local_path):
        repo.clone_success = True
        return repo
    
    try:
        # Use GIT_TERMINAL_PROMPT=0 to disable authentication prompts
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        
        result = subprocess.run(
            [
                "git", "clone",
                "--depth=1",
                "--single-branch",
                "--no-tags",
                "--quiet",
                repo.url,
                local_path
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env
        )
        repo.clone_success = result.returncode == 0
    except subprocess.TimeoutExpired:
        repo.clone_success = False
    except Exception:
        repo.clone_success = False
    
    return repo


def clone_all_repos(repos: list[RepoInfo], repos_dir: str, max_workers: int = 8) -> list[RepoInfo]:
    """Clone all repositories in parallel."""
    os.makedirs(repos_dir, exist_ok=True)
    
    print(f"Cloning {len(repos)} repositories to {repos_dir}...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(clone_repo, repo, repos_dir): repo for repo in repos}
        
        completed = 0
        for future in as_completed(futures):
            completed += 1
            if completed % 20 == 0:
                print(f"  Progress: {completed}/{len(repos)} repositories processed")
    
    successful = sum(1 for r in repos if r.clone_success)
    print(f"Successfully cloned {successful}/{len(repos)} repositories")
    
    return repos


# =============================================================================
# Parsers for different documentation formats
# =============================================================================

class BOFParser:
    """Base class for BOF parsers."""
    
    name: str = "base"
    
    def can_parse(self, repo_path: str) -> bool:
        """Check if this parser can handle this repository."""
        raise NotImplementedError
    
    def parse(self, repo_path: str, repo_url: str) -> list[BOFEntry]:
        """Parse the repository and return BOF entries."""
        raise NotImplementedError


class ReadmeTableParser(BOFParser):
    """Parse BOF information from README.md tables."""
    
    name = "readme_table"
    
    # Common table header patterns for BOF documentation (use MULTILINE for ^ to match line start)
    TABLE_HEADER_PATTERNS = [
        # |Command|Usage|Notes| (trustedsec style)
        re.compile(r'^\s*\|\s*commands?\s*\|\s*usage\s*\|', re.IGNORECASE | re.MULTILINE),
        # |Command|Description| or |Commands|Description|
        re.compile(r'^\s*\|\s*commands?\s*\|.*\|', re.IGNORECASE | re.MULTILINE),
        # |Name|Description| (outflank style)
        re.compile(r'^\s*\|\s*name\s*\|.*decr?iption.*\|', re.IGNORECASE | re.MULTILINE),
        # |BOF|Description| or |**BOF**|**Use**| (atomiczsec/Adrenaline style with bold)
        re.compile(r'^\s*\|\s*\*?\*?bof\*?\*?\s*\|.*\|', re.IGNORECASE | re.MULTILINE),
        # |Tool|Description|
        re.compile(r'^\s*\|\s*tool\s*\|.*\|', re.IGNORECASE | re.MULTILINE),
        # |Function|Description|
        re.compile(r'^\s*\|\s*function\s*\|.*\|', re.IGNORECASE | re.MULTILINE),
        # |Module|Description|
        re.compile(r'^\s*\|\s*module\s*\|.*\|', re.IGNORECASE | re.MULTILINE),
    ]
    
    # Pattern for table separator row
    TABLE_SEPARATOR = re.compile(r'^\s*\|[\s\-:|]+\|')
    
    def find_readme_files(self, repo_path: str) -> list[str]:
        """Find README files in the repository."""
        readme_files = []
        for pattern in ['README.md', 'readme.md', 'Readme.md', 'README.MD']:
            readme_path = os.path.join(repo_path, pattern)
            if os.path.exists(readme_path):
                readme_files.append(readme_path)
                break
        return readme_files
    
    def can_parse(self, repo_path: str) -> bool:
        """Check if README exists with BOF tables."""
        readme_files = self.find_readme_files(repo_path)
        if not readme_files:
            return False
        
        for readme_path in readme_files:
            try:
                with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for pattern in self.TABLE_HEADER_PATTERNS:
                        if pattern.search(content):
                            return True
            except:
                pass
        return False
    
    def parse(self, repo_path: str, repo_url: str) -> list[BOFEntry]:
        """Parse BOF entries from README tables."""
        entries = []
        readme_files = self.find_readme_files(repo_path)
        
        for readme_path in readme_files:
            try:
                with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                entries.extend(self._parse_tables(lines, readme_path, repo_url))
            except Exception as e:
                print(f"  Error parsing {readme_path}: {e}", file=sys.stderr)
        
        return entries
    
    def _parse_tables(self, lines: list[str], source_file: str, repo_url: str) -> list[BOFEntry]:
        """Extract BOF entries from markdown tables."""
        entries = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if this line is a table header we recognize
            is_header = False
            name_col_idx = 0
            desc_col_idx = 1
            
            for pattern in self.TABLE_HEADER_PATTERNS:
                if pattern.match(line):
                    is_header = True
                    # Determine column indices - strip markdown bold markers for matching
                    cols = [re.sub(r'\*+', '', c).strip().lower() for c in line.split('|')]
                    for idx, col in enumerate(cols):
                        if col in ['command', 'commands', 'name', 'bof', 'tool', 'function', 'module']:
                            name_col_idx = idx
                        elif 'description' in col or 'notes' in col or 'decription' in col or col == 'use':
                            desc_col_idx = idx
                    break
            
            if is_header:
                i += 1
                # Skip separator row
                if i < len(lines) and self.TABLE_SEPARATOR.match(lines[i]):
                    i += 1
                
                # Parse data rows
                while i < len(lines):
                    row = lines[i].strip()
                    if not row.startswith('|') or not row.endswith('|'):
                        break
                    if self.TABLE_SEPARATOR.match(row):
                        i += 1
                        continue
                    
                    cols = row.split('|')
                    if len(cols) > max(name_col_idx, desc_col_idx):
                        name = self._clean_cell(cols[name_col_idx])
                        desc = self._clean_cell(cols[desc_col_idx]) if desc_col_idx < len(cols) else ""
                        
                        # Skip if name looks like a header or is empty
                        if name and not self._is_header_like(name):
                            entries.append(BOFEntry(
                                name=name,
                                description=desc,
                                repository=repo_url,
                                source_file=os.path.basename(source_file),
                                source_format=self.name
                            ))
                    i += 1
            else:
                i += 1
        
        return entries
    
    def _clean_cell(self, cell: str) -> str:
        """Clean a table cell, removing markdown formatting."""
        cell = cell.strip()
        # Remove markdown links [text](url) -> text
        cell = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', cell)
        # Remove bold/italic
        cell = re.sub(r'\*+([^*]+)\*+', r'\1', cell)
        # Remove inline code
        cell = re.sub(r'`([^`]+)`', r'\1', cell)
        # Remove leading ** for directory-style entries
        cell = re.sub(r'^\*\*\[?', '', cell)
        cell = re.sub(r'\]?\*\*$', '', cell)
        return cell.strip()
    
    def _is_header_like(self, name: str) -> bool:
        """Check if the name looks like a header rather than a BOF name."""
        header_words = ['command', 'commands', 'name', 'bof', 'tool', 'project', '---', '===']
        return name.lower() in header_words or name.startswith('-')


class ReadmeBulletParser(BOFParser):
    """Parse BOF information from README.md bullet lists with format: - BOFName: Description"""
    
    name = "readme_bullet"
    
    # Pattern for bullet list items with BOF name and description
    # Matches: - BOFName: Description
    # Matches: - [BOFName](url): Description
    # Excludes: bold entries (typically TODOs), names with spaces, URLs, registry keys
    BULLET_PATTERN = re.compile(
        r'^\s*[-*]\s+'                        # Bullet point (- or *)
        r'(?:\[([A-Za-z][A-Za-z0-9_-]*)\]\([^)]+\)|'  # [Name](url) - name must be identifier-like
        r'([A-Za-z][A-Za-z0-9_-]*[A-Za-z0-9]))'       # Plain name (at least 2 chars, identifier-like)
        r'\s*:\s+'                             # Colon separator with required space after
        r'([A-Z].+)$',                         # Description must start with capital letter (sentence)
        re.MULTILINE                           # Allow ^ to match line starts
    )
    
    def find_readme_files(self, repo_path: str) -> list[str]:
        """Find README files in the repository."""
        readme_files = []
        for pattern in ['README.md', 'readme.md', 'Readme.md', 'README.MD']:
            readme_path = os.path.join(repo_path, pattern)
            if os.path.exists(readme_path):
                readme_files.append(readme_path)
                break
        return readme_files
    
    def can_parse(self, repo_path: str) -> bool:
        """Check if README has bullet list BOF entries."""
        readme_files = self.find_readme_files(repo_path)
        if not readme_files:
            return False
        
        for readme_path in readme_files:
            try:
                with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Need at least 1 matching bullet point to consider this format
                    matches = self.BULLET_PATTERN.findall(content)
                    if len(matches) >= 1:
                        return True
            except:
                pass
        return False
    
    def parse(self, repo_path: str, repo_url: str) -> list[BOFEntry]:
        """Parse BOF entries from README bullet lists."""
        entries = []
        readme_files = self.find_readme_files(repo_path)
        
        for readme_path in readme_files:
            try:
                with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        match = self.BULLET_PATTERN.match(line)
                        if match:
                            # Group 1 is link text, Group 2 is plain name, Group 3 is description
                            name = match.group(1) or match.group(2)
                            description = match.group(3).strip()
                            
                            # Skip common non-BOF entries
                            if self._is_generic_entry(name, description):
                                continue
                            
                            entries.append(BOFEntry(
                                name=name,
                                description=description,
                                repository=repo_url,
                                source_file=os.path.basename(readme_path),
                                source_format=self.name
                            ))
            except Exception as e:
                print(f"  Error parsing {readme_path}: {e}", file=sys.stderr)
        
        return entries
    
    def _is_generic_entry(self, name: str, description: str) -> bool:
        """Filter out common non-BOF bullet entries."""
        # Skip if name is too short (single char like 'C' for compiler)
        if len(name) <= 1:
            return True
        return False


class CNAParser(BOFParser):
    """Parse BOF information from Cobalt Strike Aggressor scripts (.cna files)."""
    
    name = "cna"
    
    # Patterns for CNA command definitions
    ALIAS_PATTERN = re.compile(r'alias\s+["\']?(\w+)["\']?\s*{')
    BEACON_CMD_PATTERN = re.compile(r'beacon_command_register\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']')
    HELP_PATTERN = re.compile(r'#\s*(.*)')  # Comments often contain descriptions
    
    def find_cna_files(self, repo_path: str) -> list[str]:
        """Find all .cna files in the repository."""
        cna_files = []
        for root, dirs, files in os.walk(repo_path):
            # Skip .git directory
            if '.git' in root:
                continue
            for f in files:
                if f.endswith('.cna'):
                    cna_files.append(os.path.join(root, f))
        return cna_files
    
    def can_parse(self, repo_path: str) -> bool:
        """Check if repository has .cna files."""
        return len(self.find_cna_files(repo_path)) > 0
    
    def parse(self, repo_path: str, repo_url: str) -> list[BOFEntry]:
        """Parse BOF entries from CNA files."""
        entries = []
        cna_files = self.find_cna_files(repo_path)
        
        for cna_path in cna_files:
            try:
                with open(cna_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Look for beacon_command_register calls (most reliable)
                for match in self.BEACON_CMD_PATTERN.finditer(content):
                    name = match.group(1).strip()
                    desc = match.group(2).strip()
                    entries.append(BOFEntry(
                        name=name,
                        description=desc,
                        repository=repo_url,
                        source_file=os.path.basename(cna_path),
                        source_format=self.name
                    ))
                
                # Also look for alias definitions with nearby help text
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    alias_match = self.ALIAS_PATTERN.search(line)
                    if alias_match:
                        name = alias_match.group(1)
                        # Look for description in previous comment lines
                        desc = ""
                        for j in range(max(0, i-3), i):
                            comment_match = self.HELP_PATTERN.match(lines[j].strip())
                            if comment_match:
                                desc = comment_match.group(1).strip()
                                break
                        
                        # Only add if not already added via beacon_command_register
                        if not any(e.name == name and e.source_file == os.path.basename(cna_path) for e in entries):
                            entries.append(BOFEntry(
                                name=name,
                                description=desc,
                                repository=repo_url,
                                source_file=os.path.basename(cna_path),
                                source_format=self.name
                            ))
            except Exception as e:
                print(f"  Error parsing {cna_path}: {e}", file=sys.stderr)
        
        return entries


class HavocPythonParser(BOFParser):
    """Parse BOF information from Havoc C2 Python extension files."""
    
    name = "havoc_py"
    
    # Patterns for Havoc Python files
    HAVOC_IMPORT = re.compile(r'(from\s+havoc\s+import|import\s+havoc)')
    # RegisterCommand( func, "module", "command", "description", ... )
    REGISTER_COMMAND_PATTERN = re.compile(
        r'RegisterCommand\s*\(\s*\w+\s*,\s*["\'][^"\']*["\']\s*,\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']*)["\']',
        re.IGNORECASE
    )
    # RegisterModule( "name", "description", ... )
    REGISTER_MODULE_PATTERN = re.compile(
        r'RegisterModule\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']*)["\']',
        re.IGNORECASE
    )
    # Older pattern: .register("name", "desc")
    REGISTER_PATTERN = re.compile(r'\.register\s*\(\s*["\']([^"\']+)["\']\s*,?\s*["\']?([^"\']*)["\']?')
    COMMAND_PATTERN = re.compile(r'["\']command["\']\s*:\s*["\']([^"\']+)["\']')
    DESCRIPTION_PATTERN = re.compile(r'["\']description["\']\s*:\s*["\']([^"\']+)["\']')
    
    def find_havoc_files(self, repo_path: str) -> list[str]:
        """Find Python files that import from havoc."""
        havoc_files = []
        for root, dirs, files in os.walk(repo_path):
            if '.git' in root:
                continue
            for f in files:
                if f.endswith('.py'):
                    file_path = os.path.join(root, f)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as fp:
                            content = fp.read(2000)  # Just check the beginning
                            if self.HAVOC_IMPORT.search(content):
                                havoc_files.append(file_path)
                    except:
                        pass
        return havoc_files
    
    def can_parse(self, repo_path: str) -> bool:
        """Check if repository has Havoc Python files."""
        return len(self.find_havoc_files(repo_path)) > 0
    
    def parse(self, repo_path: str, repo_url: str) -> list[BOFEntry]:
        """Parse BOF entries from Havoc Python files."""
        entries = []
        havoc_files = self.find_havoc_files(repo_path)
        
        for py_path in havoc_files:
            try:
                with open(py_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                seen_names = set()
                
                # Try RegisterCommand pattern first (most common in Havoc)
                for match in self.REGISTER_COMMAND_PATTERN.finditer(content):
                    name = match.group(1).strip()
                    desc = match.group(2).strip()
                    if name.lower() not in seen_names:
                        seen_names.add(name.lower())
                        entries.append(BOFEntry(
                            name=name,
                            description=desc,
                            repository=repo_url,
                            source_file=os.path.basename(py_path),
                            source_format=self.name
                        ))
                
                # Try .register pattern
                for match in self.REGISTER_PATTERN.finditer(content):
                    name = match.group(1).strip()
                    desc = match.group(2).strip() if match.group(2) else ""
                    if name.lower() not in seen_names:
                        seen_names.add(name.lower())
                        entries.append(BOFEntry(
                            name=name,
                            description=desc,
                            repository=repo_url,
                            source_file=os.path.basename(py_path),
                            source_format=self.name
                        ))
                
                # Also try dictionary-style definitions
                cmd_matches = list(self.COMMAND_PATTERN.finditer(content))
                desc_matches = list(self.DESCRIPTION_PATTERN.finditer(content))
                
                for cmd_match in cmd_matches:
                    name = cmd_match.group(1).strip()
                    desc = ""
                    # Try to find a nearby description
                    cmd_pos = cmd_match.start()
                    for desc_match in desc_matches:
                        if abs(desc_match.start() - cmd_pos) < 500:
                            desc = desc_match.group(1).strip()
                            break
                    
                    if not any(e.name == name for e in entries):
                        entries.append(BOFEntry(
                            name=name,
                            description=desc,
                            repository=repo_url,
                            source_file=os.path.basename(py_path),
                            source_format=self.name
                        ))
            except Exception as e:
                print(f"  Error parsing {py_path}: {e}", file=sys.stderr)
        
        return entries


class Stage1PythonParser(BOFParser):
    """Parse BOF information from Outflank C2 Stage1 Python files (*_bof.s1.py)."""
    
    name = "stage1_py"
    
    def find_stage1_files(self, repo_path: str) -> list[str]:
        """Find Stage1 Python files."""
        stage1_files = []
        for root, dirs, files in os.walk(repo_path):
            if '.git' in root:
                continue
            for f in files:
                if f.endswith('.s1.py') or '_bof.s1.py' in f:
                    stage1_files.append(os.path.join(root, f))
        return stage1_files
    
    def can_parse(self, repo_path: str) -> bool:
        """Check if repository has Stage1 Python files."""
        return len(self.find_stage1_files(repo_path)) > 0
    
    def parse(self, repo_path: str, repo_url: str) -> list[BOFEntry]:
        """Parse BOF entries from Stage1 Python files."""
        entries = []
        stage1_files = self.find_stage1_files(repo_path)
        
        # Patterns for Stage1 format
        name_pattern = re.compile(r'["\']?name["\']?\s*[=:]\s*["\']([^"\']+)["\']')
        desc_pattern = re.compile(r'["\']?description["\']?\s*[=:]\s*["\']([^"\']+)["\']')
        
        for s1_path in stage1_files:
            try:
                with open(s1_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Extract name and description
                name_match = name_pattern.search(content)
                desc_match = desc_pattern.search(content)
                
                if name_match:
                    name = name_match.group(1).strip()
                    desc = desc_match.group(1).strip() if desc_match else ""
                    entries.append(BOFEntry(
                        name=name,
                        description=desc,
                        repository=repo_url,
                        source_file=os.path.basename(s1_path),
                        source_format=self.name
                    ))
                else:
                    # Use filename as name
                    base_name = os.path.basename(s1_path)
                    name = base_name.replace('.s1.py', '').replace('_bof', '')
                    entries.append(BOFEntry(
                        name=name,
                        description="",
                        repository=repo_url,
                        source_file=base_name,
                        source_format=self.name
                    ))
            except Exception as e:
                print(f"  Error parsing {s1_path}: {e}", file=sys.stderr)
        
        return entries


class DirectoryStructureParser(BOFParser):
    """Infer BOF names from directory structure when no other documentation exists."""
    
    name = "directory_structure"
    
    BOF_DIR_INDICATORS = ['bof', 'bofs', 'src', 'source', 'kit', 'tools']
    BOF_FILE_PATTERNS = [
        re.compile(r'^(\w+)\.c$'),  # main.c style
        re.compile(r'^(\w+)_bof\.c$'),  # name_bof.c style
        re.compile(r'^(\w+)\.x64\.o$'),  # compiled BOF
        re.compile(r'^(\w+)\.o$'),  # compiled BOF
    ]
    
    def can_parse(self, repo_path: str) -> bool:
        """Always available as fallback."""
        return True
    
    def parse(self, repo_path: str, repo_url: str) -> list[BOFEntry]:
        """Infer BOF entries from directory structure."""
        entries = []
        seen_names = set()
        
        for root, dirs, files in os.walk(repo_path):
            if '.git' in root:
                continue
            
            # Check for source files that indicate BOF
            for f in files:
                for pattern in self.BOF_FILE_PATTERNS:
                    match = pattern.match(f)
                    if match:
                        name = match.group(1)
                        # Try to get description from parent directory or nearby README
                        desc = self._find_description(root, name)
                        
                        if name.lower() not in seen_names and len(name) > 2:
                            seen_names.add(name.lower())
                            entries.append(BOFEntry(
                                name=name,
                                description=desc,
                                repository=repo_url,
                                source_file=f,
                                source_format=self.name
                            ))
                        break
        
        return entries
    
    def _find_description(self, dir_path: str, name: str) -> str:
        """Try to find a description for the BOF."""
        # Check for a README in the same directory
        for readme_name in ['README.md', 'readme.md', 'README.txt']:
            readme_path = os.path.join(dir_path, readme_name)
            if os.path.exists(readme_path):
                try:
                    with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                        # Get first non-empty, non-header line
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                return line[:200]
                except:
                    pass
        return ""


# =============================================================================
# Main Indexer Logic
# =============================================================================

def analyze_repos(repos: list[RepoInfo]) -> dict:
    """Analyze repositories to find which parsers can handle them."""
    parsers = [
        ReadmeTableParser(),
        CNAParser(),
        HavocPythonParser(),
        Stage1PythonParser(),
        ReadmeBulletParser(),
        DirectoryStructureParser(),
    ]
    
    stats = {
        "total_repos": len(repos),
        "cloned_repos": sum(1 for r in repos if r.clone_success),
        "parseable_by_format": defaultdict(int),
        "repos_by_format": defaultdict(list),
    }
    
    for repo in repos:
        if not repo.clone_success:
            continue
        
        for parser in parsers:
            if parser.can_parse(repo.local_path):
                stats["parseable_by_format"][parser.name] += 1
                stats["repos_by_format"][parser.name].append(repo.name)
    
    return stats


def parse_all_repos(repos: list[RepoInfo], use_parsers: Optional[list[str]] = None) -> list[BOFEntry]:
    """Parse all repositories and extract BOF entries."""
    all_parsers = [
        ReadmeTableParser(),
        CNAParser(),
        HavocPythonParser(),
        Stage1PythonParser(),
        DirectoryStructureParser(),
    ]
    
    if use_parsers:
        parsers = [p for p in all_parsers if p.name in use_parsers]
    else:
        # Use all except directory_structure and readme_bullet (fallbacks only)
        parsers = [p for p in all_parsers if p.name not in ("directory_structure", "readme_bullet")]
    
    # Fallback parsers in order of preference
    readme_bullet_parser = ReadmeBulletParser()
    directory_fallback_parser = DirectoryStructureParser()
    all_entries = []
    
    for repo in repos:
        if not repo.clone_success:
            continue
        
        repo_entries = []
        formats_used = []
        
        # Try each parser
        for parser in parsers:
            if parser.can_parse(repo.local_path):
                entries = parser.parse(repo.local_path, repo.url)
                if entries:
                    repo_entries.extend(entries)
                    formats_used.append(parser.name)
        
        # If no entries found, try readme_bullet first, then directory fallback
        if not repo_entries:
            if readme_bullet_parser.can_parse(repo.local_path):
                entries = readme_bullet_parser.parse(repo.local_path, repo.url)
                if entries:
                    repo_entries.extend(entries)
                    formats_used.append(readme_bullet_parser.name)
        
        if not repo_entries:
            entries = directory_fallback_parser.parse(repo.local_path, repo.url)
            if entries:
                repo_entries.extend(entries)
                formats_used.append(directory_fallback_parser.name)
        
        repo.bofs_found = repo_entries
        repo.parse_formats_found = formats_used
        all_entries.extend(repo_entries)
    
    return all_entries


def deduplicate_entries(entries: list[BOFEntry]) -> list[BOFEntry]:
    """Remove duplicate BOF entries."""
    seen = set()
    unique_entries = []
    
    for entry in entries:
        # Key by name and repo (case-insensitive name)
        key = (entry.name.lower(), entry.repository.lower())
        if key not in seen:
            seen.add(key)
            unique_entries.append(entry)
    
    return unique_entries


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Index BOF repositories and extract BOF names/descriptions."
    )
    parser.add_argument(
        "--catalog",
        default="BOF-CATALOG.md",
        help="Path to the bofs-catalog.md file"
    )
    parser.add_argument(
        "--repos-dir",
        default="repos",
        help="Directory to clone repositories to"
    )
    parser.add_argument(
        "--output",
        default="bof-index.json",
        help="Output JSON file path"
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Only analyze formats, don't parse BOFs"
    )
    parser.add_argument(
        "--skip-clone",
        action="store_true",
        help="Skip cloning, assume repos are already present"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=8,
        help="Maximum parallel clone operations"
    )
    
    args = parser.parse_args()
    
    # Get script directory to resolve relative paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    
    catalog_path = os.path.join(root_dir, args.catalog)
    repos_dir = os.path.join(root_dir, args.repos_dir)
    output_path = os.path.join(root_dir, args.output)
    
    # Step 1: Extract URLs
    print("Step 1: Extracting repository URLs from catalog...")
    repos = extract_repo_urls_from_catalog(catalog_path)
    print(f"  Found {len(repos)} unique repositories")
    
    # Step 2: Clone repositories
    if not args.skip_clone:
        print("\nStep 2: Cloning repositories...")
        repos = clone_all_repos(repos, repos_dir, max_workers=args.max_workers)
    else:
        print("\nStep 2: Skipping clone, checking existing repos...")
        for repo in repos:
            local_path = os.path.join(repos_dir, f"{repo.owner}__{repo.name}")
            repo.local_path = local_path
            repo.clone_success = os.path.exists(local_path)
        successful = sum(1 for r in repos if r.clone_success)
        print(f"  Found {successful}/{len(repos)} repositories locally")
    
    # Step 3: Analyze formats
    print("\nStep 3: Analyzing documentation formats...")
    stats = analyze_repos(repos)
    
    print(f"\nFormat Coverage Analysis:")
    print(f"  Total repositories: {stats['total_repos']}")
    print(f"  Successfully cloned: {stats['cloned_repos']}")
    print(f"\n  Parseable by format:")
    for fmt, count in sorted(stats['parseable_by_format'].items(), key=lambda x: -x[1]):
        pct = count / stats['cloned_repos'] * 100 if stats['cloned_repos'] > 0 else 0
        print(f"    {fmt}: {count} repos ({pct:.1f}%)")
    
    if args.analyze_only:
        print("\n--analyze-only specified, stopping here.")
        return
    
    # Step 4: Parse all repositories
    print("\nStep 4: Parsing BOF entries from all repositories...")
    entries = parse_all_repos(repos)
    print(f"  Found {len(entries)} total BOF entries")
    
    # Step 5: Deduplicate
    entries = deduplicate_entries(entries)
    print(f"  After deduplication: {len(entries)} unique BOF entries")
    
    # Step 6: Output JSON
    print(f"\nStep 5: Writing output to {output_path}...")
    output_data = {
        "metadata": {
            "total_bofs": len(entries),
            "total_repos": len(repos),
            "repos_parsed": sum(1 for r in repos if r.bofs_found),
            "format_stats": dict(stats['parseable_by_format']),
        },
        "bofs": [asdict(e) for e in entries]
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nDone! BOF index written to {output_path}")
    print(f"  Total BOFs indexed: {len(entries)}")
    print(f"  Repositories with BOFs: {sum(1 for r in repos if r.bofs_found)}")


if __name__ == "__main__":
    main()

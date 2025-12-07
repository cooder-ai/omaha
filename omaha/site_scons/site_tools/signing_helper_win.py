#!/usr/bin/env python

# Copyright (c) 2024 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

"""Omaha Code Signing Helper

This module provides utilities to determine which Omaha files should be signed
during the build process. It supports wildcard patterns for flexible
file matching while maintaining security by only signing necessary files.

Usage:
    from signing_helper_win import need_sign_omaha
    
    if need_sign_omaha('/path/to/GoogleUpdate.exe'):
        # Sign the file
        sign_file(file_path)
"""

import os
import fnmatch
import subprocess


# Omaha signing whitelist (supports * and ? wildcards)
OMAHA_SIGNING_WHITELIST = [
    "*.exe",
    # Core functional DLLs that need signing
    "goopdate.dll",
    "psmachine*.dll",
    "psuser*.dll",
    # Exclude resource DLLs (goopdateres_*.dll) - they only contain UI strings
]


# Trusted certificate subjects for signature verification
OMAHA_TRUSTED_SUBJECTS = [
    'Google LLC',
    'Google Inc', 
    'Brave Software, Inc.',
    'Brave Software Inc.',
    'Microsoft Corporation',
    'Microsoft Windows',
    'GENSPARK INC.',
    'OpenJS Foundation'
]


def need_sign_omaha(file_path):
    """Check if an Omaha file should be signed based on whitelist and existing signature.
    
    Args:
        file_path (str): Path to the file to check
        
    Returns:
        bool: True if the file should be signed, False otherwise
    """
    if not file_path:
        return False
        
    # Extract filename and normalize path separators
    basename = os.path.basename(file_path.replace('\\', '/')).lower()
    
    # Only consider executables and DLLs
    if not (basename.endswith('.exe') or basename.endswith('.dll')):
        return False
    
    # Check if file matches whitelist patterns
    matches_whitelist = False
    for pattern in OMAHA_SIGNING_WHITELIST:
        if fnmatch.fnmatch(basename, pattern.lower()):
            matches_whitelist = True
            break
            
    if not matches_whitelist:
        return False
    
    # If file exists, check if it already has a trusted signature
    if os.path.exists(file_path):
        if is_signature_trusted(file_path):
            print("[omaha_signing] %s already has trusted signature, skipping" % basename)
            return False
    
    return True


def is_signature_trusted(file_path):
    """Check if a file has a trusted digital signature.
    
    Args:
        file_path (str): Path to the file to check
        
    Returns:
        bool: True if the file has a trusted signature, False otherwise
    """
    try:
        # Use PowerShell to check signature - Python 2.7 compatible
        ps_command = 'Get-AuthenticodeSignature -FilePath "%s" | Select-Object Status, SignerCertificate' % file_path
        cmd = ['powershell', '-Command', ps_command]
        
        # Python 2.7 compatible subprocess call
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            return False
            
        output = stdout.strip()
        
        # Check if signature exists (Valid, UnknownError, or any status except NotSigned)
        if 'NotSigned' in output:
            return False
            
        # Check if signer is trusted
        for trusted_subject in OMAHA_TRUSTED_SUBJECTS:
            if trusted_subject.lower() in output.lower():
                return True
                
        return False
        
    except Exception:
        # If we can't check the signature, assume it needs signing
        return False


def get_signature_info(file_path):
    """Get detailed signature information for a file.
    
    Args:
        file_path (str): Path to the file to check
        
    Returns:
        dict: Dictionary containing signature information
    """
    try:
        # Python 2.7 compatible PowerShell command
        ps_command = 'Get-AuthenticodeSignature -FilePath "%s"' % file_path
        cmd = ['powershell', '-Command', ps_command]
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            return {
                'has_signature': True,
                'output': stdout.strip(),
                'trusted': is_signature_trusted(file_path)
            }
        else:
            return {
                'has_signature': False,
                'error': stderr.strip(),
                'trusted': False
            }
            
    except Exception as e:
        return {
            'has_signature': False,
            'error': str(e),
            'trusted': False
        }


def test_omaha_whitelist():
    """Test the Omaha whitelist matching functionality."""
    test_cases = [
        # Should be signed
        ('GoogleUpdate.exe', True),
        ('GoogleUpdateOnDemand.exe', True),
        ('GoogleUpdateSetup.exe', True),
        ('GoogleUpdateCore.dll', True),
        ('goopdate.dll', True),
        ('goopdateres_en.dll', True),
        ('goopdateres_zh.dll', True),
        ('npGoogleUpdate3.dll', True),
        ('BraveUpdate.exe', True),
        ('brave_update_service.exe', True),
        ('setup.exe', True),
        ('setup_stub.exe', True),
        ('mini_installer.exe', True),
        ('omaha_unittest.exe', True),
        
        # Should NOT be signed
        ('random_file.exe', False),
        ('chrome.exe', False),
        ('notepad.exe', False),
        ('test.txt', False),
        ('', False),
        (None, False),
        
        # Test with paths
        ('/build/output/GoogleUpdate.exe', True),
        ('C:\\omaha\\build\\BraveUpdate.exe', True),
        ('/tmp/random_file.exe', False),
    ]
    
    print("Testing Omaha signing whitelist:")
    print("=" * 60)
    
    passed = 0
    total = len(test_cases)
    
    for test_input, expected in test_cases:
        try:
            result = need_sign_omaha(test_input)
            status = "PASS" if result == expected else "FAIL"
            action = "SIGN" if result else "SKIP"
            
            print("  %-30s -> %s [%s]" % (str(test_input), action, status))
            
            if result == expected:
                passed += 1
            else:
                print("    Expected: %s, Got: %s" % (expected, result))
                
        except Exception as e:
            print("  %-30s -> ERROR: %s" % (str(test_input), e))
    
    print("=" * 60)
    print("Omaha Test Results: %d/%d passed" % (passed, total))
    
    return passed == total


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Omaha Code Signing Helper')
    parser.add_argument('--test', action='store_true', help='Run whitelist tests')
    parser.add_argument('--check', metavar='FILE', help='Check if a specific file should be signed')
    parser.add_argument('--list', action='store_true', help='Show current whitelist patterns')
    parser.add_argument('--signature-info', metavar='FILE', help='Show signature information for a file')
    parser.add_argument('--is-signed', metavar='FILE', help='Check if a file is digitally signed')
    parser.add_argument('--is-trusted', metavar='FILE', help='Check if a file has a trusted signature')
    
    args = parser.parse_args()
    
    if args.test:
        test_omaha_whitelist()
    elif args.check:
        result = need_sign_omaha(args.check)
        print("File: %s" % args.check)
        print("Should be signed: %s" % ('Yes' if result else 'No'))
    elif args.list:
        print("Current Omaha signing whitelist patterns:")
        for pattern in OMAHA_SIGNING_WHITELIST:
            print("  - %s" % pattern)
    elif args.signature_info:
        info = get_signature_info(args.signature_info)
        print("Signature info for: %s" % args.signature_info)
        print("Has signature: %s" % info['has_signature'])
        if info['has_signature']:
            print("Trusted: %s" % info['trusted'])
            print("Details:\n%s" % info['output'])
        else:
            print("Error: %s" % info.get('error', 'Unknown error'))
    elif args.is_signed:
        info = get_signature_info(args.is_signed)
        print("Yes" if info['has_signature'] else "No")
    elif args.is_trusted:
        trusted = is_signature_trusted(args.is_trusted)
        print("Yes" if trusted else "No")
    else:
        parser.print_help()
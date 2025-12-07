#!/usr/bin/env python3
import uuid
import re
import sys

def generate_new_guid():
    """Generate a new GUID"""
    return str(uuid.uuid4()).upper()

def get_unmodified_guids():
    """Get the list of unmodified GUIDs to be replaced"""
    unmodified_guids = {
        # Key unmodified GUIDs extracted from analysis results
        '7CB305B1-4D45-4668-AD91-677F87BED305': 'IGoogleUpdate3',
        '1985533F-9B0F-490A-85C5-24F316E66FB2': 'IAppBundle', 
        'A4BCDF52-2179-4C77-8C5F-B8095712B563': 'IApp',
        'A147722A-5568-4B84-B401-86D744470CBF': 'IApp2',
        '4842EC21-0860-45B5-99F0-A1E6E7C11561': 'IAppCommand',
        'C11C073F-E6D0-4EF7-897B-AAF52498CD2F': 'IAppCommand2',
        'F234546B-DACD-4374-97CF-7BADFAB76766': 'IAppVersion',
        'C663DEBB-F082-4971-9F6E-35DE45C96F4E': 'IPackage',
        '48B5E6B2-9383-4B1E-AAE7-720C4779ABA6': 'IRegistrationUpdateHook',
        '660130E8-74E4-4821-A6FD-4E9A86E06470': 'ICredentialDialog',
        '24D704AD-AC42-49F2-BB4F-68BA77C98E91': 'IGoogleUpdate3WebSecurity',
        '7A24060E-533F-4962-9E15-34BD82555FA7': 'ICoCreateAsyncStatus',
        'DD84E356-3D21-44C8-83DD-6BEEC22FA427': 'ICoCreateAsync',
        'AAE4AD28-500D-43BA-9F54-730CA146C190': 'IBrowserHttpRequest2',
        '8504FB26-FC3E-4C1C-9C94-46EC93E6BA63': 'IProgressWndEvents',
        '7CFC4E00-1C9D-443D-B5BE-CEEEAC1443AF': 'IJobObserver',
        '91B050A9-5A49-4249-A8C8-B4390961A912': 'IJobObserver2',
        '4C929BFE-4FA4-488D-B1E2-82ECD6F076C8': 'IGoogleUpdate',
        '10479D64-2C5F-46CD-9BC8-FD04FF4D02D8': 'IGoogleUpdateCore',

        # Key coclasses
        '2CF4A521-EC1E-4075-A20B-5DE3E5B89B1B': 'GoogleUpdate3UserClass',
        '08F15E98-0442-45D3-82F1-F67495CC51EB': 'GoogleUpdate3ServiceClass', 
        '66CE3D6C-0B35-4F78-AC77-39728A75CB75': 'GoogleUpdate3WebMachineFallbackClass',
        '06B74C04-E813-4DD4-A972-172836EFA8D6': 'CurrentStateUserClass',
        'BC03C0E4-1528-4299-89B2-419644FA48AC': 'CurrentStateMachineClass',
        '8F6D9FE5-6ED3-43A3-80D2-EA8766D65352': 'CoCreateAsyncClass',
        '4C738ABE-2ED7-4BF6-B668-046DC1A72C00': 'CredentialDialogUserClass',
        'B5D1924F-CB80-47AA-8DEC-5E0854A42A73': 'CredentialDialogMachineClass',
        'F6E536F5-F795-49CE-A85D-2DA66503C6F1': 'PolicyStatusValueUserClass',
        'EBDA5D88-AA7D-4A8C-A20C-C01FADB43EDA': 'PolicyStatusValueMachineClass',
        '13B35483-DF37-4603-97F8-9504E48B49BF': 'PolicyStatusMachineServiceClass',
        '652886FF-517B-4F23-A14F-F99563A04BCC': 'PolicyStatusMachineFallbackClass',
        '6DA8171A-7CEC-4E45-BDED-9F287AD7C854': 'OnDemandUserAppsClass',
        '28C83F57-E4C0-4B54-B187-585C51EE8F9C': 'OnDemandMachineAppsClass',
        'D7D7525F-5DF4-4C9D-8781-C02F39F973E6': 'OnDemandMachineAppsServiceClass',
        '3282EB12-D954-4FD2-A2E1-C942C8745C65': 'OnDemandMachineAppsFallbackClass',
        '3AD2D487-D166-4160-8E36-1AE505233A55': 'GoogleUpdateCoreClass',
        'F7FF255A-A593-41BD-A69B-E05D72B72756': 'GoogleUpdateCoreMachineClass'
    }
    return unmodified_guids

def replace_guids_in_file(input_file, output_file):
    """Replace GUIDs in the file"""

    # Read the original file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    unmodified_guids = get_unmodified_guids()
    guid_mapping = {}

    # Generate a new GUID for each one to be replaced
    for old_guid, class_name in unmodified_guids.items():
        new_guid = generate_new_guid()
        guid_mapping[old_guid] = new_guid
        print(f"Replacing {class_name}: {old_guid} -> {new_guid}")

    # Perform replacements
    for old_guid, new_guid in guid_mapping.items():
        # Replace format: uuid(GUID)
        content = content.replace(f'uuid({old_guid})', f'uuid({new_guid})')
        # Also replace cases without parentheses
        content = content.replace(old_guid, new_guid)

    # Write the new file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\nReplacement completed, result saved to: {output_file}")
    print(f"Total GUIDs replaced: {len(guid_mapping)}")
    
    return guid_mapping

def main():
    input_file = 'omaha3_idl.idl'
    output_file = 'omaha3_idl_updated.idl'

    print("=== Replacing Unmodified GUIDs ===")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print("")

    try:
        guid_mapping = replace_guids_in_file(input_file, output_file)

        # Generate replacement report
        print("\n=== Replacement Report ===")
        unmodified_guids = get_unmodified_guids()
        for old_guid, new_guid in guid_mapping.items():
            class_name = unmodified_guids.get(old_guid, "Unknown")
            print(f"{class_name}:")
            print(f"  Old: {old_guid}")
            print(f"  New: {new_guid}")
            print("")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
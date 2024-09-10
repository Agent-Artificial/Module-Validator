import os
import json
from pathlib import Path


def walkdir(path):
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".json"):
                yield os.path.join(root, file)


def extract_field(data, field):
    field_data = []
    while f'"{field}": "' in data:
        try:
            block = data.split(f'"{field}": "', 1)[1]
            value, data = block.split('"', 1)
            field_data.append(value)
        except ValueError:
            break
    return field_data


def process_file(file_path):
    try:
        filepath = Path(file_path)
        if isinstance(filepath.read_text("utf-8"), str):
            data = json.loads(filepath.read_text("utf-8").strip())
        else:
            data = json.loads(filepath.read_bytes())
    except json.JSONDecodeError:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.loads(f.read().strip())
    else:

        def extract_field(data, field):
            field_data = []
            while f'"{field}": "' in data:
                try:
                    block = data.split(f'"{field}": "', 1)[1]
                    value, data = block.split('"', 1)
                    field_data.append(value)
                except ValueError:
                    break
            print(field_data)
            return field_data

    mnemonics = extract_field(data, "mnemonic")
    addresses = extract_field(data, "ss58_address")
    private_keys = extract_field(data, "private_key")
    public_keys = extract_field(data, "public_key")
    ss58_format = extract_field(data, "ss58_format")
    crypto_type = extract_field(data, "crypto_type")
    derive_path = extract_field(data, "derive_path")
    names = extract_field(data, "path")

    return (
        mnemonics,
        addresses,
        private_keys,
        public_keys,
        crypto_type,
        ss58_format,
        derive_path,
        names,
    )


def get_key_files(path, outfile):
    all_mnemonics = []
    all_addresses = []
    all_names = []
    all_derive_path = []
    all_crypto_types = []
    all_ss58_format = []
    all_public_keys = []
    all_private_keys = []

    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".json") or file.endswith(".txt"):
                file_path = os.path.join(root, file)
                try:
                    (
                        mnemonics,
                        addresses,
                        private_keys,
                        public_keys,
                        crypto_types,
                        ss58_format,
                        derive_path,
                        names,
                    ) = process_file(file_path)
                    all_mnemonics.extend(mnemonics)
                    all_addresses.extend(addresses)
                    all_names.extend(names)
                    all_derive_path.extend(derive_path)
                    all_crypto_types.extend(crypto_types)
                    all_ss58_format.extend(ss58_format)
                    all_public_keys.extend(public_keys)
                    all_private_keys.extend(private_keys)
                except Exception as e:
                    print(f"Error processing file {file}: {e}")

    key_dict = {
        all_names[i]: {
            "public_key": all_public_keys[i],
            "private_key": all_private_keys[i],
            "derive_path": all_derive_path[i],
            "crypto_type": all_crypto_types[i],
            "ss58_format": all_ss58_format[i],
            "mnemonic": all_mnemonics[i],
            "ss58_address": all_addresses[i],
        }
        for i in range(min(len(all_names), len(all_mnemonics), len(all_addresses)))
    }
    print(all_names)
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(key_dict, f, indent=4)

    return key_dict


if __name__ == "__main__":
    input_file = "key"
    output_file = "./ckeys.json"
    get_key_files(input_file, output_file)

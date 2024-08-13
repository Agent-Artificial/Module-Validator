import pkg_resources

def check_entry_points(package_name):
    print(f"Entry points for {package_name}:")
    groups = ["console_scripts", "module_validator.module", "module_validator.embedding"]
    for group in groups:
        print(f"\nGroup: {group}")
        for entry_point in pkg_resources.iter_entry_points(group):
            if entry_point.dist.project_name == package_name:
                print(f"  {entry_point.name} = {entry_point.module_name}:{entry_point.attrs[0]}")

if __name__ == "__main__":
    package_name = input("Enter the package name to check: ")
    check_entry_points(package_name)
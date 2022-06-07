import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def generate_tf_manifest_file(scopes, project_name, new_project_id, file_path=''):
    # --- Terraform manifest
    try:
        tf_manifest = f"{project_name}-env.tf"

        file_loader = FileSystemLoader('templates')
        env = Environment(loader=file_loader)
        template = env.get_template('tf_resources.j2')
        print(project_name)
        data = template.render(scopes=scopes, project_name=project_name, new_project_id=new_project_id)
        if file_path:
            write_to_file(data, file_path, tf_manifest)

    except Exception as exc:
        print("Generate manifest fail:\n" + str(exc))
        sys.exit(3)


def generate_tf_variables_records(scopes, file_path=''):
    # --- Terraform variables
    tf_variables = "variables.tf"

    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('tf_variables.j2')
    data = template.render(scopes = scopes)
    # write_to_file(jdata, './', '1234')
    if file_path:
        write_to_file(data, file_path, tf_variables)

    # print(jdata)



def generate_tf_secrets_records(scopes, project_name, file_path=''):
    # --- Sops secret variables
    tf_secrets = f"{project_name}-secrets.yaml"

    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('secrets_sops.j2')
    data = template.render(scopes = scopes)
    if file_path:
        write_to_file(data, file_path, tf_secrets)
        generate_terragrunt_records(scopes, tf_secrets, file_path)


def generate_terragrunt_records(scopes, tf_secrets, file_path=''):
    hcl_terragrunt = "terragrunt.hcl"

    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('terragrunt_hcl.j2')
    data = template.render(scopes = scopes, tf_secrets=tf_secrets)
    if file_path:
        write_to_file(data, file_path, hcl_terragrunt)


def write_to_file(data, path, filename):
    filename_with_path = f"{path}/{filename}"
    print(f'=== Write file: {filename_with_path} \n')
    try:
        # if os.path.isdir(path):
        #     shutil.rmtree(path)
        Path(path).mkdir(parents=True, exist_ok=True)

        with open(filename_with_path, 'w', encoding='utf-8') as file:
            file.write(data)
    except Exception as exc:
        print("Error write file:\n" + str(exc))
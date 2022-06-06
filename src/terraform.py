import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def generate_tf_manifest_file(scopes, project_name, new_project_id, file_path=''):
    # --- Terraform manifest
    try:
        tf_manifest = f"{project_name}-env.tf"
#         data = ''
#         for scope in scopes.keys():
#             # tf_manifest = f"{project_name}-env-{scope.lower()}.tf"
#             print(f"======== {scope}")
#             print(f"=== Terraform manifest file: {tf_manifest} Content file:")
#             data += '''resource "gitlab_project_variable" "%s-%s" {
#   for_each          = local.%s-%s
#   project           = "%s"
#   key               = each.key
#   value             = each.value
#   protected         = false
#   environment_scope = "%s"
# }
# ''' % (project_name, scope.lower(), project_name, scope.lower(), new_project_id, scope)
#             print(data)
#             data += '''
# locals {
#   %s-%s = {\n''' % (project_name, scope.lower())
#
#             for variable in scopes[scope]['variables']:
#                 data += f"    {variable['key']} = \"{variable['value']}\"\n"
#             for secrets in scopes[scope]['secrets']:
#                 data += f"    {secrets['key']} = \"{secrets['manifest_var']}\"\n"
#             data += '  }\n}\n\n'
#             print(data)
#         if file_path:
#             write_to_file(data, file_path, tf_manifest)
        file_loader = FileSystemLoader('src/templates')
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
    # data = ''
    # for scope in scopes.keys():
    #     print(f"======== {scope}")
    #     print(f"=== Terraform variables file: {tf_variables} Content file:\n")
    #     for secrets in scopes[scope]['secrets']:
    #         data += secrets['variables_var'] + "\n"
    #     print(data)
    file_loader = FileSystemLoader('src/templates')
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
    # data = ''
    # for scope in scopes.keys():
    #     print(f"======== {scope}")
    #     print(f"=== Terraform secrets(sops) file: {tf_secrets} Content file:\n")
    #     if len(scopes[scope]['secrets']) > 0:
    #         for secrets in scopes[scope]['secrets']:
    #             data += secrets['secrets_var'] + "\n"
    #         print(data)
    file_loader = FileSystemLoader('src/templates')
    env = Environment(loader=file_loader)
    template = env.get_template('secrets_sops.j2')
    data = template.render(scopes = scopes)
    if file_path:
        write_to_file(data, file_path, tf_secrets)
        generate_terragrunt_records(scopes, tf_secrets, file_path)


def generate_terragrunt_records(scopes, tf_secrets, file_path=''):
    hcl_terragrunt = "terragrunt.hcl"
    # data = 'inputs = {\n'
    # for scope in scopes.keys():
    #     if len(scopes[scope]['secrets']) > 0:
    #         print(f"======== {scope}")
    #         print(f"=== Terraform terragrunt.hcl file: {hcl_terragrunt} Content file:\n")
    #         # data += f"# ----- {}"
    #         for secrets in scopes[scope]['secrets']:
    #             data += f"  {secrets['terragrunt_var'].replace('secret_file_name', tf_secrets)} \n"
    #         print(data)
    # data += "}"
    # print(data)
    file_loader = FileSystemLoader('src/templates')
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
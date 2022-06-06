#!python3

from pathlib import Path
import sys, traceback
import terraform
import gitlab


def sort_data(
    project_name,
    new_project_id='',
):
    var_project_name = project_name.replace("-", "_").upper()
    project_id = gitlab.search("projects", project_name)[0]["id"]

    cicd_variables = gitlab.get_project_variables(project_id)

    env_scopes = []

    variables = []
    for variables in cicd_variables:
        if variables["environment_scope"] == "*":
            variables["environment_scope"] = "ALL"
        env_scopes.append(variables["environment_scope"])
    env_scopes = set(env_scopes)

    scopes = {
        #'project_name': project_name,
        #'project_id': project_id
    }  # {"project_name": name, "PROD": {"variables": [], secrets: [] }
    # if new_project_id:
    #     scopes.update({'new_project_id': new_project_id})
    # secrets_pattern = ["PASSWORD", "USERNAME", "RSA". 'KEY', 'SECRET']

    # --- Make records
    secrets_var = []
    for scope in env_scopes:
        scopes.update(
            {
                scope: {
                    "variables": [],
                    "secrets": [],
                }
            }
        )
        for variables in cicd_variables:
            if variables["environment_scope"] == scope:
                key = variables["key"]
                val = variables["value"]
                if (
                    "username" in key.lower()
                    or "password" in key.lower()
                    or "rsa" in key.lower()
                    or "key" in key.lower()
                    or "secret" in key.lower()
                ):
                    # print(scope, key)
                    if '\n' in val:
                        val = val.replace('\n', '\n  ')
                    scopes[scope]["secrets"].append(
                        {
                            "key": key,
                            "value": val,
                            'variable_with_env': f"{var_project_name}_{key}_{scope}",
                        }
                    )
                else:
                    scopes[scope]["variables"].append(
                        {"key": key, "value": val}
                    )
    return scopes


if __name__ == "__main__":
    project_name = "fxbison"  # ToDo In run argument
    new_project_id = 371
    scopes = sort_data(project_name)

    terraform.generate_tf_manifest_file(
        scopes, project_name, new_project_id, project_name
    )
    terraform.generate_tf_variables_records(scopes, project_name)
    terraform.generate_tf_secrets_records(scopes, project_name, project_name)

    # ToDo: running arguments:
    # ToDo: --project {name|id} String
    # ToDo: --new-id 123 Integer
    # from jinja2 import Environment, FileSystemLoader
    # file_loader = FileSystemLoader('templates')
    # env = Environment(loader=file_loader)
    # template = env.get_template('resource.j2')
    # print(template.render(project_name=project_name, variables=scopes['UAT']['variables']))
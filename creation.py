import os

import yaml
from jinja2 import Template


def create_namespaces(config_data):
    output_directory = 'namespace'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open('namespace_template.yml', 'r') as namespace_file:
        namespace_template_content = namespace_file.read()

    environments = config_data['environments']
    namespace_name = config_data['namespace_name']
    environment = config_data['environment']

    namespace_template = Template(namespace_template_content)

    for i in range(environments):
        namespace_concat = f"{namespace_name}-{i}"

        namespace_output = namespace_template.render(
            namespace_name=namespace_concat,
            namespace_environment=environment
        )

        with open(f'namespace/namespace_{i}.yml', 'w') as output_file:
            output_file.write(namespace_output)

    print(f"{environments} namespaces created successfully.")

def create_deployments(config_data):
    output_directory = 'deployments'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open('deployment_template.yml', 'r') as deployment_file:
        deployment_template_content = deployment_file.read()

    environments = config_data['environments']
    machines = config_data['machines']
    replicas = config_data['replicas']
    kali_config = config_data['kali_config']
    ubuntu_config = config_data['ubuntu_config']

    deployment_template = Template(deployment_template_content)

    for i in range(environments):
        kali_num = 0
        ubuntu_num = 0

        for machine in machines:
            sub_output_directory = f'{output_directory}/deployment_{i}'
            if not os.path.exists(sub_output_directory):
                os.makedirs(sub_output_directory)

            if machine == "kali":
                kali_num += 1
                machine_name_concat = f"{machine}-{i}-{kali_num}"
                config = kali_config

            elif machine == "ubuntu":
                ubuntu_num += 1
                machine_name_concat = f"{machine}-{i}-{ubuntu_num}"
                config = ubuntu_config

            container_image = config['image']
            env_variables = config.get('env', [])
            container_args = config.get('container_commands', [])
            container_port = config['ports'][0]['container_port']
            service_account_name = config['service_account_name']
            service_account_enabled = config.get('service_account', False)
            role_rules = config.get('role_rules', [])
            service_port = config.get('service_port', 80)
            service_type = config.get('service_type', 'ClusterIP')

            namespace = f'{config_data["namespace_name"]}-{i}'
            deployment_name = f'{machine_name_concat}-deployment'
            role_name = f"{machine_name_concat}-role" if service_account_enabled else None
            rolebinding_name = f"{machine_name_concat}-rolebinding" if service_account_enabled else None
            service_name = f"{machine_name_concat}-service"

            deployment_output = deployment_template.render(
                deployment_name=deployment_name,
                namespace=namespace,
                app_label=machine_name_concat,
                replicas=replicas,
                container_image=container_image,
                service_account_name=service_account_name if service_account_enabled else None,
                env_variables=env_variables,
                container_args="\n".join(container_args),
                container_port=container_port,
                role_name=role_name,
                rolebinding_name=rolebinding_name,
                service_name=service_name,
                role_rules=role_rules,
                service_port=service_port,
                service_type=service_type,
                service_account_enabled=service_account_enabled  # Pass whether service account is enabled
            )

            with open(f'{sub_output_directory}/deployment_{machine}_{i}.yml', 'w') as output_file:
                output_file.write(deployment_output)

    print(f"Deployments created for {environments} environments successfully.")

def main():
    with open('config.yml', 'r') as config_file:
        config_data = yaml.safe_load(config_file)

    create_namespaces(config_data)
    create_deployments(config_data)

if __name__ == '__main__':
    main()

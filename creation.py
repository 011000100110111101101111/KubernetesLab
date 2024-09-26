import json
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

    deployment_template = Template(deployment_template_content)

    machine_counters = {}

    for i in range(environments):
        environment_dir = os.path.join(output_directory, f"env-{i+1}")
        if not os.path.exists(environment_dir):
            os.makedirs(environment_dir)

        for j, machine in enumerate(machines):

            machine_config = config_data.get(f"{machine}_config", None)

            if not machine_config:
                print(f"Warning: No config found for machine '{machine}'")
                continue

            if machine not in machine_counters:
                machine_counters[machine] = 0

            # Increment the counter for the machine type
            machine_counters[machine] += 1
            machine_name_concat = f"{machine}-{i}-{machine_counters[machine]}"

            container_image = machine_config['image']
            env_variables = machine_config.get('env', [])
            container_args = machine_config.get('container_commands', [])
            container_port = machine_config['ports'][0]['container_port']
            service_account_name = machine_config['service_account_name']
            service_account_enabled = machine_config['service_account']
            role_rules = machine_config.get('role_rules', [])
            service_port = machine_config['ports'][0]['service_port']
            service_type = machine_config.get('service_type', 'ClusterIP')
            network_policy = machine_config.get('network_policy', {})

            namespace = f'{config_data["namespace_name"]}-{i}'
            deployment_name = f'{machine_name_concat}-deployment'
            role_name = f"{machine_name_concat}-role" if service_account_enabled else None
            rolebinding_name = f"{machine_name_concat}-rolebinding" if service_account_enabled else None
            service_name = f"{machine_name_concat}-service"
            network_policy_name = f"{machine_name_concat}-networkpolicy"
            firewall_enabled = machine_config['firewall_enabled']
            firewall_label = machine_config['firewall_label']
            config_map_enabled = machine_config['config_map_enabled']
            config_map = machine_config['config_map'] if config_map_enabled else None

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
                network_policy=network_policy,
                network_policy_name=network_policy_name,
                service_account_enabled=service_account_enabled,
                firewall_enabled=firewall_enabled,
                firewall_label=firewall_label,
                config_map=config_map
            )

            # Write each machine deployment to a unique file
            with open(f'{environment_dir}/deployment_{machine}_{i}_{machine_counters[machine]}.yml', 'w') as output_file:
                output_file.write(deployment_output)

    print(f"Deployments created for {environments} environments successfully.")

def main():
    with open('config.yml', 'r') as config_file:
        config_data = yaml.safe_load(config_file)

    create_namespaces(config_data)
    create_deployments(config_data)

if __name__ == '__main__':
    main()

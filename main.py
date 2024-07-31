from kubernetes import client, config
import yaml
import json


class KubernetesResources:
    """
    One class to rule them all.
    """
    def __init__(self):
        self.apps_client = client.AppsV1Api()
        self.core_client = client.CoreV1Api()
        self.networking_client = client.NetworkingV1Api()
        self.output_struct = {
            "Namespaces" : list()
        }

    def dump_output_struct(self):
        print(yaml.dump(self.output_struct))

    def populate_namespaces(self):
        r = self.core_client.list_namespace()
        self.all_namespaces = [n.metadata.name for n in r.items]

    def get_namespaced_deployments(self):
        """
        Returns all deployment objects in a namespace.
        """
        return self.apps_client.list_namespaced_deployment(self.current_namespace)

    def init_namespace_list(self):
        """ Initializes the namespace list of resources. """
        self.output_struct["Namespaces"].append({self.current_namespace : list()})

    def init_deployment_list(self):
        """ Initializes the namespace list of resources. """
        self.output_struct["Namespaces"][-1][self.current_namespace].append({"Deployments" : list()})

    def add_deployment_to_output_struct(self, deployment):
        """ Filters necessary deployment data and appents the deployment object to the list. """

        deployment_dict = deployment.to_dict()
        deployment_dict.pop("api_version")
        deployment_dict.pop("kind")
        deployment_dict.pop("status")

        metadata_keys_to_remove = [
            "deletion_grace_period_seconds",
            "deletion_timestamp",
            "finalizers",
            "generate_name",
            "managed_fields",
            "owner_references",
            "resource_version",
            "self_link",
            "uid"
        ]

        spec_keys_to_remove = [
            "min_ready_seconds",
            "paused",
            "progress_deadline_seconds",
            "revision_history_limit",
        ]

        spec_template_keys_to_remove = [
            "metadata"
        ]

        # TODO: unfold
        spec_template_spec_keys_to_remove = [
            'active_deadline_seconds',
            'automount_service_account_token',
            'dns_config',
            'dns_policy',
            'enable_service_links', 'ephemeral_containers', 'host_aliases', 'host_ipc', 'host_network', 'host_pid', 'host_users', 'hostname', 'image_pull_secrets', 'init_containers', 'node_name', 'node_selector', 'os', 'overhead', 'preemption_policy', 'priority', 'priority_class_name', 'readiness_gates', 'resource_claims', 'restart_policy', 'runtime_class_name', 'scheduler_name', 'scheduling_gates', 'security_context', 'service_account', 'service_account_name', 'set_hostname_as_fqdn', 'share_process_namespace', 'subdomain', 'termination_grace_period_seconds', 'tolerations', 'topology_spread_constraints' 
        ]

        # Remove unecessary top level metadata keys
        for k in metadata_keys_to_remove:
            deployment_dict["metadata"].pop(k)

        # Remove unecessary top level spec keys
        for k in spec_keys_to_remove:
            deployment_dict["spec"].pop(k)

        # Remove duplicated metadata from spec
        for k in spec_template_keys_to_remove:
            deployment_dict["spec"]["template"].pop(k)

        # Remove redundant keys from spec->template->spec
        for k in spec_template_spec_keys_to_remove:
            deployment_dict["spec"]["template"]["spec"].pop(k)

        self.output_struct["Namespaces"][-1][self.current_namespace][-1]["Deployments"][-1].update(deployment_dict)


    def construct_all_deployments_in_all_namespaces(self):
        """
        Adds all deployments for all namespaces into the output struct - YAML.
        OUTPUT: YAML output of deployment object
        """

        self.populate_namespaces()
        for ns_name in self.all_namespaces:
            self.current_namespace = ns_name
            self.init_namespace_list()
            self.init_deployment_list()
            namespaced_deployments = self.get_namespaced_deployments()

            api_version = namespaced_deployments.api_version
            kind = namespaced_deployments.kind
            deployment_header = {
                "apiVersion" : api_version,
                "kind" : kind
            }

            for each_deployment in namespaced_deployments.items:
                self.output_struct["Namespaces"][-1][self.current_namespace][-1]["Deployments"].append(deployment_header)
                self.add_deployment_to_output_struct(each_deployment)
            

def main():

    # Use current_context from ~/.kubeconfig
    # TODO: move into class
    config.load_kube_config()

    kuberes = KubernetesResources()
    kuberes.construct_all_deployments_in_all_namespaces()


if __name__ == "__main__":
    main()

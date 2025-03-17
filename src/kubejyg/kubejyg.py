from kubernetes import client, config
import yaml
import json
import argparse
import os


class KubejygHelpFormatter (argparse.HelpFormatter):
    """
    Argparse formatter
    """

    def _split_lines(self, text, width):
        return super()._split_lines(text, width) + [""]

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
        self.all_namespaces = []

    def dump_output_struct_yaml(self):
        print(yaml.dump(self.output_struct))

    def dump_output_struct_json(self):
        print(json.dumps(self.output_struct, indent=4, default=str))

    def populate_namespaces(self):
        if len(self.all_namespaces) == 0:
            r = self.core_client.list_namespace()
            self.all_namespaces = [n.metadata.name for n in r.items]

    def get_namespaced_deployments(self):
        """
        Returns all deployment objects in the current namespace.
        """
        return self.apps_client.list_namespaced_deployment(self.current_namespace)

    def get_namespaced_services(self):
        """
        Returns all service objects in the current namespace.
        """
        return self.core_client.list_namespaced_service(self.current_namespace)

    def get_namespaced_ingress(self):
        """
        Returns all ingress objects in the current namespace.
        """
        return self.networking_client.list_namespaced_ingress(self.current_namespace)

    def add_current_namespace_to_output_struct(self):
        """
        1. Check if output_struct["Namespaces"] is empty and add the current namespace as last - update current_namespace_index
        2. If output_struct["Namespaces"] not empty:
            2.1 Check if dicts in output_struct["Namespaces"] contain the namespace
            2.2 If namespace is found - update current_namespace_index
            2.3 If namespace is NOT found - append current_namespacec - update current_namespace_index
        """

        if len(self.output_struct["Namespaces"]) == 0:
            # If namespaces empty, initialize with current namespace
            self.output_struct["Namespaces"].append({self.current_namespace : list()})
            self.current_namespace_index = -1
        else:
            namespace_found = False
            for i in range(len(self.output_struct["Namespaces"])):
                if self.current_namespace in self.output_struct["Namespaces"][i].keys():
                    namespace_found = True
                    self.current_namespace_index = i
                    break
            if namespace_found == False:
                self.output_struct["Namespaces"].append({self.current_namespace : list()})
                self.current_namespace_index = -1

    # TODO: make this function generic and reduce - Pass type of resource to expand the list.
    def init_deployment_list(self):
        """ Initializes the namespace list of resources. """
        self.output_struct["Namespaces"][self.current_namespace_index][self.current_namespace].append({"Deployments" : list()})

    def init_service_list(self):
        """ Initializes the namespaced list of resources. """
        self.output_struct["Namespaces"][self.current_namespace_index][self.current_namespace].append({"Services" : list()})

    def init_ingress_list(self):
        """ Initializes the namespace list of resources. """
        self.output_struct["Namespaces"][self.current_namespace_index][self.current_namespace].append({"Ingress" : list()})


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

        self.output_struct["Namespaces"][self.current_namespace_index][self.current_namespace][-1]["Deployments"][-1].update(deployment_dict)

    def add_service_to_output_struct(self, service):
        """ Filters necessary deployment data and appents the deployment object to the list. """

        service_dict = service.to_dict()
        service_dict.pop("api_version")
        service_dict.pop("kind")
        service_dict.pop("status")

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
            service_dict["metadata"].pop(k)

        self.output_struct["Namespaces"][self.current_namespace_index][self.current_namespace][-1]["Services"][-1].update(service_dict)


    def add_ingress_to_output_struct(self, ingress):
        """ Filters necessary ingress data and appends the ingress object to the list. """

        ingress_dict = ingress.to_dict()
        ingress_dict.pop("api_version")
        ingress_dict.pop("kind")
        ingress_dict.pop("status")

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
            ingress_dict["metadata"].pop(k)

        # Remove unecessary top level spec keys
        #for k in spec_keys_to_remove:
        #    ingress_dict["spec"].pop(k)

        # Remove duplicated metadata from spec
        #for k in spec_template_keys_to_remove:
        #    ingress_dict["spec"]["template"].pop(k)

        # Remove redundant keys from spec->template->spec
        #for k in spec_template_spec_keys_to_remove:
        #    ingress_dict["spec"]["template"]["spec"].pop(k)

        self.output_struct["Namespaces"][self.current_namespace_index][self.current_namespace][-1]["Ingress"][-1].update(ingress_dict)


    # TODO: See if you can reduce duplication with these functions - individual resource fetching.
    def construct_all_deployments_in_all_namespaces(self):
        """
        Adds all deployments for all namespaces into the output struct - YAML.
        """
        self.populate_namespaces()
        for ns_name in self.all_namespaces:
            self.current_namespace = ns_name
            namespaced_deployments = self.get_namespaced_deployments()
            if len(namespaced_deployments.items) != 0:
                self.add_current_namespace_to_output_struct()
                self.init_deployment_list()
                for each_deployment in namespaced_deployments.items:
                    deployment_header = {
                        "apiVersion" : "apps/v1",
                        "kind" : "Deployment" 
                    }
                    self.output_struct["Namespaces"][self.current_namespace_index][self.current_namespace][-1]["Deployments"].append(deployment_header)
                    self.add_deployment_to_output_struct(each_deployment)


    def construct_all_services_in_all_namespaces(self):
        """
        Adds all services for all namespaces into the output struct - YAML.
        """
        self.populate_namespaces()
        for ns_name in self.all_namespaces:
            self.current_namespace = ns_name
            namespaced_services = self.get_namespaced_services()
            if len(namespaced_services.items) != 0:
                self.add_current_namespace_to_output_struct()
                self.init_service_list()
                for each_service in namespaced_services.items:
                    service_header = {
                        "apiVersion" : "v1",
                        "kind" : "Service"
                    }
                    self.output_struct["Namespaces"][self.current_namespace_index][self.current_namespace][-1]["Services"].append(service_header)
                    self.add_service_to_output_struct(each_service)
            
    def construct_all_ingress_in_all_namespaces(self):
        """
        Adds all ingress for all namespaces into the output struct - YAML.
        """
        self.populate_namespaces()
        for ns_name in self.all_namespaces:
            self.current_namespace = ns_name
            namespaced_ingress = self.get_namespaced_ingress()
            if len(namespaced_ingress.items) != 0:
                self.add_current_namespace_to_output_struct()
                self.init_ingress_list()
                for each_ingress in namespaced_ingress.items:
                    ingress_header = {
                        "apiVersion" : "networking.k8s.io/v1",
                        "kind" : "Ingress" 
                    }
                    self.output_struct["Namespaces"][self.current_namespace_index][self.current_namespace][-1]["Ingress"].append(ingress_header)
                    self.add_ingress_to_output_struct(each_ingress)


def validate_kubeconfig(config):
    """
    Validate if provided kubeconfig exists - exit if not.
    """
    if not os.path.exists(os.path.expanduser(config)):
        print(f"kubeconfig: cannot access {config}: No such file")
        exit(1)

    if not os.path.isfile(os.path.expanduser(config)):
        print(f"kubeconfig: {config} is not a file.")
        exit(2)

    if os.path.getsize(os.path.expanduser(config)) == 0:
        print(f"kubeconfig: {config}: is empty")
        exit(3)


def main():
    parser = argparse.ArgumentParser(
        prog="kubejyg",
        usage='%(prog)s [options]',
        description="Kubernetes Resource Extraction with Namespace Grouping ready for filtering with jq, yq and grep.",
        conflict_handler="error",
        add_help=True,
        formatter_class=KubejygHelpFormatter
        )
    parser.add_argument("-o", "--output", type=str, required=False, choices=["json", "yaml"], help="Output in JSON or (default) YAML format.")
    parser.add_argument("-kc", "--kubeconfig", type=str, required=False, default=os.environ.get('KUBECONFIG', '~/.kube/config'), help="Kubernetes config file.")
    args = parser.parse_args()

    validate_kubeconfig(args.kubeconfig)
    config.load_kube_config(config_file=args.kubeconfig)

    kuberes = KubernetesResources()
    kuberes.construct_all_deployments_in_all_namespaces()
    kuberes.construct_all_services_in_all_namespaces()
    kuberes.construct_all_ingress_in_all_namespaces()

    if args.output == "json":
        kuberes.dump_output_struct_json()
    else:
        kuberes.dump_output_struct_yaml()


if __name__ == "__main__":
    main()

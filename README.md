# Kubejyg
##### _Kubernetes Resource Extraction with Namespace Grouping._

## How it works

`kubejyg` extracts `Kubernetes` resources across multiple namespaces, grouping them by `namespace`. The output is generated in either `JSON` or `YAML`, ready to be piped into well known processors like `jq`, `yq`, and `grep`.

**Examples**

Fetch all deployment manifests from all namespaces in YAML.

```bash
kubejyg | yq ".Namespaces.[].[].[].Deployments" -C
```

Fetch all deployment manifests across all namespaces in YAML and filter nulls.

```bash
kubejyg | yq ".Namespaces[].[].[].Deployments | select ( . != null ) | .[]" -C
```

Fetch all the annotations from all the Services across all Namespaces in JSON.

```bash
kubejyg -o json | jq ".Namespaces[].[].[].Services | select ( . != null) | .[].metadata.annotations" -C
```

## Output structure

```json
{
    "Namespaces": [
        {
            "ns-1": [
                {
                    "Deployments": [
                        {
                            deployment-manifest-1
                        }
                        ...
                    ]
                    "Services": [
                        {
                            service-manifest-1
                        }
                        ...
                    ]
                    "Ingress": [
                        {
                            ingress-manifest-1
                        }
                        ...
                    ]
                }
            ]
        ...
        }
    ]
}
```

## Installation

```bash
pip install kubejyg
```

## Features

**Kubernetes resources**:
- Deployments
- Services
- Ingresses

**Output**:
- YAML
- JSON

## Naming

**kubejyg** is named after the following utilities:
1. `kubectl`
2. `jq`
3. `yq`
4. `grep`

## Gotchas

`jq: error (at <stdin>:1): Cannot iterate over null (null)`.

Some namespaces might not contain resources of all kinds. If we apply filters over empty arrays, `jq` and `yq` will replaces those arrays with `null` values. Applying filters over them will error out. Use `select ( . != null)` to filter `null` expressions, **see examples for details**.


## Contributing

1. Create an issue
2. Fork
3. Change
4. Open PR
5. Profit!


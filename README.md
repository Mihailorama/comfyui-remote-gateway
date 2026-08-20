# ComfyUI Remote Gateway

Fail-closed routing policy for remote ComfyUI jobs.

This package is the independent Python policy core. It has no provider
credentials, no GPU deployment template and no ComfyUI-loaded custom node.
Remote execution requires both server policy and an explicit request from the
browser. Invalid workflow references or a profile outside the allowlist fail
closed.

## Install

~~~bash
pip install comfyui-remote-gateway
~~~

## Example

~~~python
from comfyui_remote_gateway import RemotePolicy, route

policy = RemotePolicy.from_names(("image", "video"))
request = {
    "client_id": "operator-17",
    "prompt": {"1": {"class_type": "KSampler", "inputs": {}}},
    "extra_data": {"comfyui_remote": {"enabled": True, "profile": "image"}},
}

remote_job = route(request, policy, server_enabled=True)
assert remote_job is not None
assert remote_job.profile.name == "image"
~~~

## Scope

This is not a ComfyUI extension and does not redistribute ComfyUI or custom
nodes. Keep an integration that is loaded by ComfyUI, and any built image,
under its own file-level license and provenance review. The reference
implementation in this repository is MIT; it does not change the license of
ComfyUI or other components used by an integrator.

## Development

~~~bash
PYTHONPATH=src python -m unittest discover -s tests -v
uv build
~~~

## License

MIT. See [LICENSE](LICENSE).

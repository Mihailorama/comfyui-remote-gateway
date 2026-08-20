"""Fail-closed routing policy for remote ComfyUI jobs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


class RemoteRoutingError(ValueError):
    """A request cannot be safely routed to remote execution."""


@dataclass(frozen=True)
class ComputeProfile:
    name: str


@dataclass(frozen=True)
class RemotePolicy:
    profiles: Mapping[str, ComputeProfile]

    @classmethod
    def from_names(cls, names: tuple[str, ...] | list[str]) -> "RemotePolicy":
        values = tuple(names)
        if not values or any(not name.strip() for name in values) or len(set(values)) != len(values):
            raise ValueError("profiles must be unique, non-empty names")
        return cls({name: ComputeProfile(name) for name in values})


@dataclass(frozen=True)
class RemoteRequest:
    workflow: dict[str, dict[str, Any]]
    profile: ComputeProfile
    client_id: str


def _validate_workflow(workflow: object) -> dict[str, dict[str, Any]]:
    if not isinstance(workflow, dict) or not workflow:
        raise RemoteRoutingError("prompt must contain a non-empty API-format workflow")
    node_ids = set(workflow)
    if any(not isinstance(node_id, str) or not node_id for node_id in node_ids):
        raise RemoteRoutingError("workflow node IDs must be non-empty strings")
    for node_id, node in workflow.items():
        if not isinstance(node, dict):
            raise RemoteRoutingError(f"workflow node {node_id!r} must be an object")
        class_type = node.get("class_type")
        inputs = node.get("inputs")
        if not isinstance(class_type, str) or not class_type.strip():
            raise RemoteRoutingError(f"workflow node {node_id!r} has no class_type")
        if not isinstance(inputs, dict):
            raise RemoteRoutingError(f"workflow node {node_id!r} inputs must be an object")
        for value in inputs.values():
            if (
                isinstance(value, list)
                and len(value) == 2
                and isinstance(value[0], str)
                and isinstance(value[1], int)
                and value[0] not in node_ids
            ):
                raise RemoteRoutingError(
                    f"workflow node {node_id!r} references missing node {value[0]!r}"
                )
    return workflow


def route(
    request: Mapping[str, Any],
    policy: RemotePolicy,
    *,
    server_enabled: bool,
) -> RemoteRequest | None:
    """Return a validated remote request only after both explicit opt-ins."""

    if not server_enabled:
        return None
    extra_data = request.get("extra_data") or {}
    if not isinstance(extra_data, dict):
        raise RemoteRoutingError("extra_data must be an object")
    routing = extra_data.get("comfyui_remote")
    if routing is None:
        return None
    if not isinstance(routing, dict):
        raise RemoteRoutingError("extra_data.comfyui_remote must be an object")
    enabled = routing.get("enabled", False)
    if not isinstance(enabled, bool):
        raise RemoteRoutingError("remote enabled flag must be boolean")
    if not enabled:
        return None
    profile_name = routing.get("profile")
    if not isinstance(profile_name, str) or profile_name not in policy.profiles:
        raise RemoteRoutingError("remote profile is not allowed by the server policy")
    client_id = request.get("client_id") or extra_data.get("client_id")
    if not isinstance(client_id, str) or not client_id or len(client_id) > 128:
        raise RemoteRoutingError("remote prompts require a valid client_id")
    return RemoteRequest(
        workflow=_validate_workflow(request.get("prompt")),
        profile=policy.profiles[profile_name],
        client_id=client_id,
    )


__all__ = [
    "ComputeProfile",
    "RemotePolicy",
    "RemoteRequest",
    "RemoteRoutingError",
    "route",
]

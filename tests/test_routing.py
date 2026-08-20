import unittest

import comfyui_remote_gateway


class RemoteRoutingContractTest(unittest.TestCase):
    def test_remote_route_requires_server_and_browser_opt_in(self) -> None:
        request = {
            "client_id": "creator-1",
            "prompt": {"1": {"class_type": "KSampler", "inputs": {}}},
            "extra_data": {"comfyui_remote": {"enabled": True, "profile": "image"}},
        }
        policy = comfyui_remote_gateway.RemotePolicy.from_names(("image",))

        self.assertIsNone(comfyui_remote_gateway.route(request, policy, server_enabled=False))
        routed = comfyui_remote_gateway.route(request, policy, server_enabled=True)
        self.assertEqual(routed.profile.name, "image")
        self.assertEqual(routed.client_id, "creator-1")

    def test_remote_route_rejects_unknown_profile_and_invalid_workflow_reference(self) -> None:
        policy = comfyui_remote_gateway.RemotePolicy.from_names(("image",))
        unknown_profile = {
            "client_id": "creator-1",
            "prompt": {"1": {"class_type": "KSampler", "inputs": {}}},
            "extra_data": {"comfyui_remote": {"enabled": True, "profile": "video"}},
        }
        missing_reference = {
            "client_id": "creator-1",
            "prompt": {"1": {"class_type": "KSampler", "inputs": {"model": ["99", 0]}}},
            "extra_data": {"comfyui_remote": {"enabled": True, "profile": "image"}},
        }

        with self.assertRaises(comfyui_remote_gateway.RemoteRoutingError):
            comfyui_remote_gateway.route(unknown_profile, policy, server_enabled=True)
        with self.assertRaises(comfyui_remote_gateway.RemoteRoutingError):
            comfyui_remote_gateway.route(missing_reference, policy, server_enabled=True)

# Copyright 2024 The YASTN Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
""" change device/dtype with .to()"""
import pytest
import yastn
try:
    from .configs import config_U1
except ImportError:
    from configs import  config_U1

tol = 1e-12  #pylint: disable=invalid-name


@pytest.mark.skipif(config_U1.backend.BACKEND_ID=="numpy", reason="numpy works on single device and does not have problems with promoting types")
def test_to():
    leg = yastn.Leg(config_U1, s=1, t=(-1, 0, 1), D=(1, 2, 3))
    ta = yastn.rand(config=config_U1, legs=[leg, leg, leg.conj()], dtype='float64', device='cpu')

    tb = ta.to(dtype='complex128')
    assert tb.yast_dtype == 'complex128'
    assert tb.dtype == config_U1.backend.DTYPE['complex128']
    assert tb.is_consistent()

    if config_U1.backend.torch.cuda.is_available():
        tc = ta.to(device='cuda:0')
        assert tc.device == 'cuda:0'
        assert tc.yast_dtype == 'float64'
        assert tc.dtype == config_U1.backend.DTYPE['float64']
        assert tc.is_consistent()

        td = ta.to(device='cuda:0', dtype='complex128')
        assert td.device == 'cuda:0'
        assert td.yast_dtype == 'complex128'
        assert td.dtype == config_U1.backend.DTYPE['complex128']
        assert td.is_consistent()


if __name__ == '__main__':
    test_to()

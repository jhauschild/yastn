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
import argparse
import time

a_data_size= 922753
a_order=(0, 2, 4, 5, 1, 3)
a_meta_new=(((-4, 4), (12552, 4), (0, 50208)), ((-2, 2), (18416, 8), (50208, 197536)), ((0, 0), (22128, 16), (197536, 551584)), ((2, -2), (21144, 12), (551584, 805312)), ((4, -4), (16537, 9), (805312, 954145)))
a_meta_mrg=(((-4, 4), (55284, 56580), (6, 2, 3, 2, 3, 6), ((0, 324), (0, 4)), (324, 4)), ((-4, 4), (56580, 58020), (6, 2, 3, 2, 2, 10), ((324, 684), (0, 4)), (360, 4)), ((-4, 4), (58020, 60468), (6, 2, 3, 2, 2, 17), ((684, 1296), (0, 4)), (612, 4)), ((-4, 4), (67476, 68916), (6, 2, 2, 2, 3, 10), ((1296, 1656), (0, 4)), (360, 4)), ((-4, 4), (68916, 70548), (6, 2, 2, 2, 2, 17), ((1656, 2064), (0, 4)), (408, 4)), ((-4, 4), (70548, 71508), (6, 2, 2, 2, 2, 10), ((2064, 2304), (0, 4)), (240, 4)), ((-4, 4), (74820, 77268), (6, 2, 2, 2, 3, 17), ((2304, 2916), (0, 4)), (612, 4)), ((-4, 4), (77268, 78228), (6, 2, 2, 2, 2, 10), ((2916, 3156), (0, 4)), (240, 4)), ((-4, 4), (78228, 78804), (6, 2, 2, 2, 2, 6), ((3156, 3300), (0, 4)), (144, 4)), ((-4, 4), (226424, 227864), (10, 2, 3, 2, 2, 6), ((3300, 3660), (0, 4)), (360, 4)), ((-4, 4), (227864, 230264), (10, 2, 3, 2, 2, 10), ((3660, 4260), (0, 4)), (600, 4)), ((-4, 4), (246944, 248384), (10, 2, 2, 2, 3, 6), ((4260, 4620), (0, 4)), (360, 4)), ((-4, 4), (248384, 249984), (10, 2, 2, 2, 2, 10), ((4620, 5020), (0, 4)), (400, 4)), ((-4, 4), (249984, 252704), (10, 2, 2, 2, 2, 17), ((5020, 5700), (0, 4)), (680, 4)), ((-4, 4), (264384, 266784), (10, 2, 2, 2, 3, 10), ((5700, 6300), (0, 4)), (600, 4)), ((-4, 4), (266784, 269504), (10, 2, 2, 2, 2, 17), ((6300, 6980), (0, 4)), (680, 4)), ((-4, 4), (269504, 271104), (10, 2, 2, 2, 2, 10), ((6980, 7380), (0, 4)), (400, 4)), ((-4, 4), (579773, 582221), (17, 2, 3, 2, 2, 6), ((7380, 7992), (0, 4)), (612, 4)), ((-4, 4), (609149, 610781), (17, 2, 2, 2, 2, 6), ((7992, 8400), (0, 4)), (408, 4)), ((-4, 4), (610781, 613501), (17, 2, 2, 2, 2, 10), ((8400, 9080), (0, 4)), (680, 4)), ((-4, 4), (641857, 644305), (17, 2, 2, 2, 3, 6), ((9080, 9692), (0, 4)), (612, 4)), ((-4, 4), (644305, 647025), (17, 2, 2, 2, 2, 10), ((9692, 10372), (0, 4)), (680, 4)), ((-4, 4), (647025, 651649), (17, 2, 2, 2, 2, 17), ((10372, 11528), (0, 4)), (1156, 4)), ((-4, 4), (824589, 825549), (10, 2, 2, 2, 2, 6), ((11528, 11768), (0, 4)), (240, 4)), ((-4, 4), (841389, 842349), (10, 2, 2, 2, 2, 6), ((11768, 12008), (0, 4)), (240, 4)), ((-4, 4), (842349, 843949), (10, 2, 2, 2, 2, 10), ((12008, 12408), (0, 4)), (400, 4)), ((-4, 4), (922177, 922753), (6, 2, 2, 2, 2, 6), ((12408, 12552), (0, 4)), (144, 4)), ((-2, 2), (26928, 29088), (6, 2, 3, 2, 3, 10), ((0, 540), (0, 4)), (540, 4)), ((-2, 2), (29088, 31536), (6, 2, 3, 2, 2, 17), ((540, 1152), (0, 4)), (612, 4)), ((-2, 2), (31536, 32976), (6, 2, 3, 2, 2, 10), ((1152, 1512), (0, 4)), (360, 4)), ((-2, 2), (36288, 38736), (6, 2, 2, 2, 3, 17), ((1512, 2124), (0, 4)), (612, 4)), ((-2, 2), (38736, 39696), (6, 2, 2, 2, 2, 10), ((2124, 2364), (0, 4)), (240, 4)), ((-2, 2), (39696, 40272), (6, 2, 2, 2, 2, 6), ((2364, 2508), (0, 4)), (144, 4)), ((-2, 2), (49236, 51396), (6, 2, 3, 2, 3, 10), ((0, 540), (4, 8)), (540, 4)), ((-2, 2), (51396, 53844), (6, 2, 3, 2, 2, 17), ((540, 1152), (4, 8)), (612, 4)), ((-2, 2), (53844, 55284), (6, 2, 3, 2, 2, 10), ((1152, 1512), (4, 8)), (360, 4)), ((-2, 2), (63492, 65940), (6, 2, 2, 2, 3, 17), ((1512, 2124), (4, 8)), (612, 4)), ((-2, 2), (65940, 66900), (6, 2, 2, 2, 2, 10), ((2124, 2364), (4, 8)), (240, 4)), ((-2, 2), (66900, 67476), (6, 2, 2, 2, 2, 6), ((2364, 2508), (4, 8)), (144, 4)), ((-2, 2), (72804, 74244), (6, 2, 2, 2, 3, 10), ((2508, 2868), (4, 8)), (360, 4)), ((-2, 2), (74244, 74820), (6, 2, 2, 2, 2, 6), ((2868, 3012), (4, 8)), (144, 4)), ((-2, 2), (163464, 165624), (10, 2, 3, 2, 3, 6), ((3012, 3552), (0, 4)), (540, 4)), ((-2, 2), (165624, 168024), (10, 2, 3, 2, 2, 10), ((3552, 4152), (0, 4)), (600, 4)), ((-2, 2), (168024, 172104), (10, 2, 3, 2, 2, 17), ((4152, 5172), (0, 4)), (1020, 4)), ((-2, 2), (183784, 186184), (10, 2, 2, 2, 3, 10), ((5172, 5772), (0, 4)), (600, 4)), ((-2, 2), (186184, 188904), (10, 2, 2, 2, 2, 17), ((5772, 6452), (0, 4)), (680, 4)), ((-2, 2), (188904, 190504), (10, 2, 2, 2, 2, 10), ((6452, 6852), (0, 4)), (400, 4)), ((-2, 2), (196024, 200104), (10, 2, 2, 2, 3, 17), ((6852, 7872), (0, 4)), (1020, 4)), ((-2, 2), (200104, 201704), (10, 2, 2, 2, 2, 10), ((7872, 8272), (0, 4)), (400, 4)), ((-2, 2), (201704, 202664), (10, 2, 2, 2, 2, 6), ((8272, 8512), (0, 4)), (240, 4)), ((-2, 2), (217784, 219944), (10, 2, 3, 2, 3, 6), ((3012, 3552), (4, 8)), (540, 4)), ((-2, 2), (219944, 222344), (10, 2, 3, 2, 2, 10), ((3552, 4152), (4, 8)), (600, 4)), ((-2, 2), (222344, 226424), (10, 2, 3, 2, 2, 17), ((4152, 5172), (4, 8)), (1020, 4)), ((-2, 2), (240224, 242624), (10, 2, 2, 2, 3, 10), ((5172, 5772), (4, 8)), (600, 4)), ((-2, 2), (242624, 245344), (10, 2, 2, 2, 2, 17), ((5772, 6452), (4, 8)), (680, 4)), ((-2, 2), (245344, 246944), (10, 2, 2, 2, 2, 10), ((6452, 6852), (4, 8)), (400, 4)), ((-2, 2), (257744, 261824), (10, 2, 2, 2, 3, 17), ((6852, 7872), (4, 8)), (1020, 4)), ((-2, 2), (261824, 263424), (10, 2, 2, 2, 2, 10), ((7872, 8272), (4, 8)), (400, 4)), ((-2, 2), (263424, 264384), (10, 2, 2, 2, 2, 6), ((8272, 8512), (4, 8)), (240, 4)), ((-2, 2), (475257, 477705), (17, 2, 3, 2, 2, 6), ((8512, 9124), (0, 4)), (612, 4)), ((-2, 2), (477705, 481785), (17, 2, 3, 2, 2, 10), ((9124, 10144), (0, 4)), (1020, 4)), ((-2, 2), (510141, 512589), (17, 2, 2, 2, 3, 6), ((10144, 10756), (0, 4)), (612, 4)), ((-2, 2), (512589, 515309), (17, 2, 2, 2, 2, 10), ((10756, 11436), (0, 4)), (680, 4)), ((-2, 2), (515309, 519933), (17, 2, 2, 2, 2, 17), ((11436, 12592), (0, 4)), (1156, 4)), ((-2, 2), (539789, 543869), (17, 2, 2, 2, 3, 10), ((12592, 13612), (0, 4)), (1020, 4)), ((-2, 2), (543869, 548493), (17, 2, 2, 2, 2, 17), ((13612, 14768), (0, 4)), (1156, 4)), ((-2, 2), (548493, 551213), (17, 2, 2, 2, 2, 10), ((14768, 15448), (0, 4)), (680, 4)), ((-2, 2), (573245, 575693), (17, 2, 3, 2, 2, 6), ((8512, 9124), (4, 8)), (612, 4)), ((-2, 2), (575693, 579773), (17, 2, 3, 2, 2, 10), ((9124, 10144), (4, 8)), (1020, 4)), ((-2, 2), (599357, 601805), (17, 2, 2, 2, 3, 6), ((10144, 10756), (4, 8)), (612, 4)), ((-2, 2), (601805, 604525), (17, 2, 2, 2, 2, 10), ((10756, 11436), (4, 8)), (680, 4)), ((-2, 2), (604525, 609149), (17, 2, 2, 2, 2, 17), ((11436, 12592), (4, 8)), (1156, 4)), ((-2, 2), (630433, 634513), (17, 2, 2, 2, 3, 10), ((12592, 13612), (4, 8)), (1020, 4)), ((-2, 2), (634513, 639137), (17, 2, 2, 2, 2, 17), ((13612, 14768), (4, 8)), (1156, 4)), ((-2, 2), (639137, 641857), (17, 2, 2, 2, 2, 10), ((14768, 15448), (4, 8)), (680, 4)), ((-2, 2), (771109, 772549), (10, 2, 3, 2, 2, 6), ((15448, 15808), (0, 4)), (360, 4)), ((-2, 2), (788389, 789349), (10, 2, 2, 2, 2, 6), ((15808, 16048), (0, 4)), (240, 4)), ((-2, 2), (789349, 790949), (10, 2, 2, 2, 2, 10), ((16048, 16448), (0, 4)), (400, 4)), ((-2, 2), (807629, 809069), (10, 2, 2, 2, 3, 6), ((16448, 16808), (0, 4)), (360, 4)), ((-2, 2), (809069, 810669), (10, 2, 2, 2, 2, 10), ((16808, 17208), (0, 4)), (400, 4)), ((-2, 2), (810669, 813389), (10, 2, 2, 2, 2, 17), ((17208, 17888), (0, 4)), (680, 4)), ((-2, 2), (822029, 822989), (10, 2, 2, 2, 2, 6), ((15808, 16048), (4, 8)), (240, 4)), ((-2, 2), (822989, 824589), (10, 2, 2, 2, 2, 10), ((16048, 16448), (4, 8)), (400, 4)), ((-2, 2), (835629, 837069), (10, 2, 2, 2, 3, 6), ((16448, 16808), (4, 8)), (360, 4)), ((-2, 2), (837069, 838669), (10, 2, 2, 2, 2, 10), ((16808, 17208), (4, 8)), (400, 4)), ((-2, 2), (838669, 841389), (10, 2, 2, 2, 2, 17), ((17208, 17888), (4, 8)), (680, 4)), ((-2, 2), (903841, 904417), (6, 2, 2, 2, 2, 6), ((17888, 18032), (0, 4)), (144, 4)), ((-2, 2), (913921, 914497), (6, 2, 2, 2, 2, 6), ((18032, 18176), (0, 4)), (144, 4)), ((-2, 2), (914497, 915457), (6, 2, 2, 2, 2, 10), ((18176, 18416), (0, 4)), (240, 4)), ((-2, 2), (920641, 921217), (6, 2, 2, 2, 2, 6), ((18032, 18176), (4, 8)), (144, 4)), ((-2, 2), (921217, 922177), (6, 2, 2, 2, 2, 10), ((18176, 18416), (4, 8)), (240, 4)), ((0, 0), (7452, 12960), (6, 3, 3, 2, 3, 17), ((0, 918), (0, 6)), (918, 6)), ((0, 0), (12960, 15120), (6, 3, 3, 2, 2, 10), ((918, 1278), (0, 6)), (360, 6)), ((0, 0), (15120, 16416), (6, 3, 3, 2, 2, 6), ((1278, 1494), (0, 6)), (216, 6)), ((0, 0), (20952, 24624), (6, 2, 3, 2, 3, 17), ((0, 918), (6, 10)), (918, 4)), ((0, 0), (24624, 26064), (6, 2, 3, 2, 2, 10), ((918, 1278), (6, 10)), (360, 4)), ((0, 0), (26064, 26928), (6, 2, 3, 2, 2, 6), ((1278, 1494), (6, 10)), (216, 4)), ((0, 0), (34272, 35712), (6, 2, 2, 2, 3, 10), ((1494, 1854), (6, 10)), (360, 4)), ((0, 0), (35712, 36288), (6, 2, 2, 2, 2, 6), ((1854, 1998), (6, 10)), (144, 4)), ((0, 0), (40272, 45780), (6, 2, 3, 3, 3, 17), ((0, 918), (10, 16)), (918, 6)), ((0, 0), (45780, 47940), (6, 2, 3, 3, 2, 10), ((918, 1278), (10, 16)), (360, 6)), ((0, 0), (47940, 49236), (6, 2, 3, 3, 2, 6), ((1278, 1494), (10, 16)), (216, 6)), ((0, 0), (60468, 62628), (6, 2, 2, 3, 3, 10), ((1494, 1854), (10, 16)), (360, 6)), ((0, 0), (62628, 63492), (6, 2, 2, 3, 2, 6), ((1854, 1998), (10, 16)), (144, 6)), ((0, 0), (71508, 72804), (6, 2, 2, 3, 3, 6), ((1998, 2214), (10, 16)), (216, 6)), ((0, 0), (105084, 110484), (10, 3, 3, 2, 3, 10), ((2214, 3114), (0, 6)), (900, 6)), ((0, 0), (110484, 116604), (10, 3, 3, 2, 2, 17), ((3114, 4134), (0, 6)), (1020, 6)), ((0, 0), (116604, 120204), (10, 3, 3, 2, 2, 10), ((4134, 4734), (0, 6)), (600, 6)), ((0, 0), (128484, 134604), (10, 3, 2, 2, 3, 17), ((4734, 5754), (0, 6)), (1020, 6)), ((0, 0), (134604, 137004), (10, 3, 2, 2, 2, 10), ((5754, 6154), (0, 6)), (400, 6)), ((0, 0), (137004, 138444), (10, 3, 2, 2, 2, 6), ((6154, 6394), (0, 6)), (240, 6)), ((0, 0), (153384, 156984), (10, 2, 3, 2, 3, 10), ((2214, 3114), (6, 10)), (900, 4)), ((0, 0), (156984, 161064), (10, 2, 3, 2, 2, 17), ((3114, 4134), (6, 10)), (1020, 4)), ((0, 0), (161064, 163464), (10, 2, 3, 2, 2, 10), ((4134, 4734), (6, 10)), (600, 4)), ((0, 0), (177144, 181224), (10, 2, 2, 2, 3, 17), ((4734, 5754), (6, 10)), (1020, 4)), ((0, 0), (181224, 182824), (10, 2, 2, 2, 2, 10), ((5754, 6154), (6, 10)), (400, 4)), ((0, 0), (182824, 183784), (10, 2, 2, 2, 2, 6), ((6154, 6394), (6, 10)), (240, 4)), ((0, 0), (192664, 195064), (10, 2, 2, 2, 3, 10), ((6394, 6994), (6, 10)), (600, 4)), ((0, 0), (195064, 196024), (10, 2, 2, 2, 2, 6), ((6994, 7234), (6, 10)), (240, 4)), ((0, 0), (202664, 208064), (10, 2, 3, 3, 3, 10), ((2214, 3114), (10, 16)), (900, 6)), ((0, 0), (208064, 214184), (10, 2, 3, 3, 2, 17), ((3114, 4134), (10, 16)), (1020, 6)), ((0, 0), (214184, 217784), (10, 2, 3, 3, 2, 10), ((4134, 4734), (10, 16)), (600, 6)), ((0, 0), (230264, 236384), (10, 2, 2, 3, 3, 17), ((4734, 5754), (10, 16)), (1020, 6)), ((0, 0), (236384, 238784), (10, 2, 2, 3, 2, 10), ((5754, 6154), (10, 16)), (400, 6)), ((0, 0), (238784, 240224), (10, 2, 2, 3, 2, 6), ((6154, 6394), (10, 16)), (240, 6)), ((0, 0), (252704, 256304), (10, 2, 2, 3, 3, 10), ((6394, 6994), (10, 16)), (600, 6)), ((0, 0), (256304, 257744), (10, 2, 2, 3, 2, 6), ((6994, 7234), (10, 16)), (240, 6)), ((0, 0), (334905, 340413), (17, 3, 3, 2, 3, 6), ((7234, 8152), (0, 6)), (918, 6)), ((0, 0), (340413, 346533), (17, 3, 3, 2, 2, 10), ((8152, 9172), (0, 6)), (1020, 6)), ((0, 0), (346533, 356937), (17, 3, 3, 2, 2, 17), ((9172, 10906), (0, 6)), (1734, 6)), ((0, 0), (386721, 392841), (17, 3, 2, 2, 3, 10), ((10906, 11926), (0, 6)), (1020, 6)), ((0, 0), (392841, 399777), (17, 3, 2, 2, 2, 17), ((11926, 13082), (0, 6)), (1156, 6)), ((0, 0), (399777, 403857), (17, 3, 2, 2, 2, 10), ((13082, 13762), (0, 6)), (680, 6)), ((0, 0), (417933, 428337), (17, 3, 2, 2, 3, 17), ((13762, 15496), (0, 6)), (1734, 6)), ((0, 0), (428337, 432417), (17, 3, 2, 2, 2, 10), ((15496, 16176), (0, 6)), (680, 6)), ((0, 0), (432417, 434865), (17, 3, 2, 2, 2, 6), ((16176, 16584), (0, 6)), (408, 6)), ((0, 0), (460569, 464241), (17, 2, 3, 2, 3, 6), ((7234, 8152), (6, 10)), (918, 4)), ((0, 0), (464241, 468321), (17, 2, 3, 2, 2, 10), ((8152, 9172), (6, 10)), (1020, 4)), ((0, 0), (468321, 475257), (17, 2, 3, 2, 2, 17), ((9172, 10906), (6, 10)), (1734, 4)), ((0, 0), (498717, 502797), (17, 2, 2, 2, 3, 10), ((10906, 11926), (6, 10)), (1020, 4)), ((0, 0), (502797, 507421), (17, 2, 2, 2, 2, 17), ((11926, 13082), (6, 10)), (1156, 4)), ((0, 0), (507421, 510141), (17, 2, 2, 2, 2, 10), ((13082, 13762), (6, 10)), (680, 4)), ((0, 0), (528501, 535437), (17, 2, 2, 2, 3, 17), ((13762, 15496), (6, 10)), (1734, 4)), ((0, 0), (535437, 538157), (17, 2, 2, 2, 2, 10), ((15496, 16176), (6, 10)), (680, 4)), ((0, 0), (538157, 539789), (17, 2, 2, 2, 2, 6), ((16176, 16584), (6, 10)), (408, 4)), ((0, 0), (551213, 556721), (17, 2, 3, 3, 3, 6), ((7234, 8152), (10, 16)), (918, 6)), ((0, 0), (556721, 562841), (17, 2, 3, 3, 2, 10), ((8152, 9172), (10, 16)), (1020, 6)), ((0, 0), (562841, 573245), (17, 2, 3, 3, 2, 17), ((9172, 10906), (10, 16)), (1734, 6)), ((0, 0), (582221, 588341), (17, 2, 2, 3, 3, 10), ((10906, 11926), (10, 16)), (1020, 6)), ((0, 0), (588341, 595277), (17, 2, 2, 3, 2, 17), ((11926, 13082), (10, 16)), (1156, 6)), ((0, 0), (595277, 599357), (17, 2, 2, 3, 2, 10), ((13082, 13762), (10, 16)), (680, 6)), ((0, 0), (613501, 623905), (17, 2, 2, 3, 3, 17), ((13762, 15496), (10, 16)), (1734, 6)), ((0, 0), (623905, 627985), (17, 2, 2, 3, 2, 10), ((15496, 16176), (10, 16)), (680, 6)), ((0, 0), (627985, 630433), (17, 2, 2, 3, 2, 6), ((16176, 16584), (10, 16)), (408, 6)), ((0, 0), (687289, 689449), (10, 3, 3, 2, 2, 6), ((16584, 16944), (0, 6)), (360, 6)), ((0, 0), (689449, 693049), (10, 3, 3, 2, 2, 10), ((16944, 17544), (0, 6)), (600, 6)), ((0, 0), (718069, 720229), (10, 3, 2, 2, 3, 6), ((17544, 17904), (0, 6)), (360, 6)), ((0, 0), (720229, 722629), (10, 3, 2, 2, 2, 10), ((17904, 18304), (0, 6)), (400, 6)), ((0, 0), (722629, 726709), (10, 3, 2, 2, 2, 17), ((18304, 18984), (0, 6)), (680, 6)), ((0, 0), (744229, 747829), (10, 3, 2, 2, 3, 10), ((18984, 19584), (0, 6)), (600, 6)), ((0, 0), (747829, 751909), (10, 3, 2, 2, 2, 17), ((19584, 20264), (0, 6)), (680, 6)), ((0, 0), (751909, 754309), (10, 3, 2, 2, 2, 10), ((20264, 20664), (0, 6)), (400, 6)), ((0, 0), (767269, 768709), (10, 2, 3, 2, 2, 6), ((16584, 16944), (6, 10)), (360, 4)), ((0, 0), (768709, 771109), (10, 2, 3, 2, 2, 10), ((16944, 17544), (6, 10)), (600, 4)), ((0, 0), (782629, 784069), (10, 2, 2, 2, 3, 6), ((17544, 17904), (6, 10)), (360, 4)), ((0, 0), (784069, 785669), (10, 2, 2, 2, 2, 10), ((17904, 18304), (6, 10)), (400, 4)), ((0, 0), (785669, 788389), (10, 2, 2, 2, 2, 17), ((18304, 18984), (6, 10)), (680, 4)), ((0, 0), (800909, 803309), (10, 2, 2, 2, 3, 10), ((18984, 19584), (6, 10)), (600, 4)), ((0, 0), (803309, 806029), (10, 2, 2, 2, 2, 17), ((19584, 20264), (6, 10)), (680, 4)), ((0, 0), (806029, 807629), (10, 2, 2, 2, 2, 10), ((20264, 20664), (6, 10)), (400, 4)), ((0, 0), (813389, 815549), (10, 2, 2, 3, 3, 6), ((17544, 17904), (10, 16)), (360, 6)), ((0, 0), (815549, 817949), (10, 2, 2, 3, 2, 10), ((17904, 18304), (10, 16)), (400, 6)), ((0, 0), (817949, 822029), (10, 2, 2, 3, 2, 17), ((18304, 18984), (10, 16)), (680, 6)), ((0, 0), (825549, 829149), (10, 2, 2, 3, 3, 10), ((18984, 19584), (10, 16)), (600, 6)), ((0, 0), (829149, 833229), (10, 2, 2, 3, 2, 17), ((19584, 20264), (10, 16)), (680, 6)), ((0, 0), (833229, 835629), (10, 2, 2, 3, 2, 10), ((20264, 20664), (10, 16)), (400, 6)), ((0, 0), (859069, 860365), (6, 3, 3, 2, 2, 6), ((20664, 20880), (0, 6)), (216, 6)), ((0, 0), (874621, 875485), (6, 3, 2, 2, 2, 6), ((20880, 21024), (0, 6)), (144, 6)), ((0, 0), (875485, 876925), (6, 3, 2, 2, 2, 10), ((21024, 21264), (0, 6)), (240, 6)), ((0, 0), (891937, 893233), (6, 3, 2, 2, 3, 6), ((21264, 21480), (0, 6)), (216, 6)), ((0, 0), (893233, 894673), (6, 3, 2, 2, 2, 10), ((21480, 21720), (0, 6)), (240, 6)), ((0, 0), (894673, 897121), (6, 3, 2, 2, 2, 17), ((21720, 22128), (0, 6)), (408, 6)), ((0, 0), (902305, 902881), (6, 2, 2, 2, 2, 6), ((20880, 21024), (6, 10)), (144, 4)), ((0, 0), (902881, 903841), (6, 2, 2, 2, 2, 10), ((21024, 21264), (6, 10)), (240, 4)), ((0, 0), (910465, 911329), (6, 2, 2, 2, 3, 6), ((21264, 21480), (6, 10)), (216, 4)), ((0, 0), (911329, 912289), (6, 2, 2, 2, 2, 10), ((21480, 21720), (6, 10)), (240, 4)), ((0, 0), (912289, 913921), (6, 2, 2, 2, 2, 17), ((21720, 22128), (6, 10)), (408, 4)), ((0, 0), (915457, 916753), (6, 2, 2, 3, 3, 6), ((21264, 21480), (10, 16)), (216, 6)), ((0, 0), (916753, 918193), (6, 2, 2, 3, 2, 10), ((21480, 21720), (10, 16)), (240, 6)), ((0, 0), (918193, 920641), (6, 2, 2, 3, 2, 17), ((21720, 22128), (10, 16)), (408, 6)), ((2, -2), (2916, 6156), (6, 3, 3, 2, 3, 10), ((0, 540), (0, 6)), (540, 6)), ((2, -2), (6156, 7452), (6, 3, 3, 2, 2, 6), ((540, 756), (0, 6)), (216, 6)), ((2, -2), (16416, 19656), (6, 2, 3, 3, 3, 10), ((0, 540), (6, 12)), (540, 6)), ((2, -2), (19656, 20952), (6, 2, 3, 3, 2, 6), ((540, 756), (6, 12)), (216, 6)), ((2, -2), (32976, 34272), (6, 2, 2, 3, 3, 6), ((756, 972), (6, 12)), (216, 6)), ((2, -2), (90144, 99324), (10, 3, 3, 2, 3, 17), ((972, 2502), (0, 6)), (1530, 6)), ((2, -2), (99324, 102924), (10, 3, 3, 2, 2, 10), ((2502, 3102), (0, 6)), (600, 6)), ((2, -2), (102924, 105084), (10, 3, 3, 2, 2, 6), ((3102, 3462), (0, 6)), (360, 6)), ((2, -2), (123444, 127044), (10, 3, 2, 2, 3, 10), ((3462, 4062), (0, 6)), (600, 6)), ((2, -2), (127044, 128484), (10, 3, 2, 2, 2, 6), ((4062, 4302), (0, 6)), (240, 6)), ((2, -2), (138444, 147624), (10, 2, 3, 3, 3, 17), ((972, 2502), (6, 12)), (1530, 6)), ((2, -2), (147624, 151224), (10, 2, 3, 3, 2, 10), ((2502, 3102), (6, 12)), (600, 6)), ((2, -2), (151224, 153384), (10, 2, 3, 3, 2, 6), ((3102, 3462), (6, 12)), (360, 6)), ((2, -2), (172104, 175704), (10, 2, 2, 3, 3, 10), ((3462, 4062), (6, 12)), (600, 6)), ((2, -2), (175704, 177144), (10, 2, 2, 3, 2, 6), ((4062, 4302), (6, 12)), (240, 6)), ((2, -2), (190504, 192664), (10, 2, 2, 3, 3, 6), ((4302, 4662), (6, 12)), (360, 6)), ((2, -2), (309201, 318381), (17, 3, 3, 2, 3, 10), ((4662, 6192), (0, 6)), (1530, 6)), ((2, -2), (318381, 328785), (17, 3, 3, 2, 2, 17), ((6192, 7926), (0, 6)), (1734, 6)), ((2, -2), (328785, 334905), (17, 3, 3, 2, 2, 10), ((7926, 8946), (0, 6)), (1020, 6)), ((2, -2), (369789, 380193), (17, 3, 2, 2, 3, 17), ((8946, 10680), (0, 6)), (1734, 6)), ((2, -2), (380193, 384273), (17, 3, 2, 2, 2, 10), ((10680, 11360), (0, 6)), (680, 6)), ((2, -2), (384273, 386721), (17, 3, 2, 2, 2, 6), ((11360, 11768), (0, 6)), (408, 6)), ((2, -2), (409365, 415485), (17, 3, 2, 2, 3, 10), ((11768, 12788), (0, 6)), (1020, 6)), ((2, -2), (415485, 417933), (17, 3, 2, 2, 2, 6), ((12788, 13196), (0, 6)), (408, 6)), ((2, -2), (434865, 444045), (17, 2, 3, 3, 3, 10), ((4662, 6192), (6, 12)), (1530, 6)), ((2, -2), (444045, 454449), (17, 2, 3, 3, 2, 17), ((6192, 7926), (6, 12)), (1734, 6)), ((2, -2), (454449, 460569), (17, 2, 3, 3, 2, 10), ((7926, 8946), (6, 12)), (1020, 6)), ((2, -2), (481785, 492189), (17, 2, 2, 3, 3, 17), ((8946, 10680), (6, 12)), (1734, 6)), ((2, -2), (492189, 496269), (17, 2, 2, 3, 2, 10), ((10680, 11360), (6, 12)), (680, 6)), ((2, -2), (496269, 498717), (17, 2, 2, 3, 2, 6), ((11360, 11768), (6, 12)), (408, 6)), ((2, -2), (519933, 526053), (17, 2, 2, 3, 3, 10), ((11768, 12788), (6, 12)), (1020, 6)), ((2, -2), (526053, 528501), (17, 2, 2, 3, 2, 6), ((12788, 13196), (6, 12)), (408, 6)), ((2, -2), (674329, 677569), (10, 3, 3, 2, 3, 6), ((13196, 13736), (0, 6)), (540, 6)), ((2, -2), (677569, 681169), (10, 3, 3, 2, 2, 10), ((13736, 14336), (0, 6)), (600, 6)), ((2, -2), (681169, 687289), (10, 3, 3, 2, 2, 17), ((14336, 15356), (0, 6)), (1020, 6)), ((2, -2), (707989, 711589), (10, 3, 2, 2, 3, 10), ((15356, 15956), (0, 6)), (600, 6)), ((2, -2), (711589, 715669), (10, 3, 2, 2, 2, 17), ((15956, 16636), (0, 6)), (680, 6)), ((2, -2), (715669, 718069), (10, 3, 2, 2, 2, 10), ((16636, 17036), (0, 6)), (400, 6)), ((2, -2), (734269, 740389), (10, 3, 2, 2, 3, 17), ((17036, 18056), (0, 6)), (1020, 6)), ((2, -2), (740389, 742789), (10, 3, 2, 2, 2, 10), ((18056, 18456), (0, 6)), (400, 6)), ((2, -2), (742789, 744229), (10, 3, 2, 2, 2, 6), ((18456, 18696), (0, 6)), (240, 6)), ((2, -2), (754309, 757549), (10, 2, 3, 3, 3, 6), ((13196, 13736), (6, 12)), (540, 6)), ((2, -2), (757549, 761149), (10, 2, 3, 3, 2, 10), ((13736, 14336), (6, 12)), (600, 6)), ((2, -2), (761149, 767269), (10, 2, 3, 3, 2, 17), ((14336, 15356), (6, 12)), (1020, 6)), ((2, -2), (772549, 776149), (10, 2, 2, 3, 3, 10), ((15356, 15956), (6, 12)), (600, 6)), ((2, -2), (776149, 780229), (10, 2, 2, 3, 2, 17), ((15956, 16636), (6, 12)), (680, 6)), ((2, -2), (780229, 782629), (10, 2, 2, 3, 2, 10), ((16636, 17036), (6, 12)), (400, 6)), ((2, -2), (790949, 797069), (10, 2, 2, 3, 3, 17), ((17036, 18056), (6, 12)), (1020, 6)), ((2, -2), (797069, 799469), (10, 2, 2, 3, 2, 10), ((18056, 18456), (6, 12)), (400, 6)), ((2, -2), (799469, 800909), (10, 2, 2, 3, 2, 6), ((18456, 18696), (6, 12)), (240, 6)), ((2, -2), (855613, 856909), (6, 3, 3, 2, 2, 6), ((18696, 18912), (0, 6)), (216, 6)), ((2, -2), (856909, 859069), (6, 3, 3, 2, 2, 10), ((18912, 19272), (0, 6)), (360, 6)), ((2, -2), (869437, 870733), (6, 3, 2, 2, 3, 6), ((19272, 19488), (0, 6)), (216, 6)), ((2, -2), (870733, 872173), (6, 3, 2, 2, 2, 10), ((19488, 19728), (0, 6)), (240, 6)), ((2, -2), (872173, 874621), (6, 3, 2, 2, 2, 17), ((19728, 20136), (0, 6)), (408, 6)), ((2, -2), (885889, 888049), (6, 3, 2, 2, 3, 10), ((20136, 20496), (0, 6)), (360, 6)), ((2, -2), (888049, 890497), (6, 3, 2, 2, 2, 17), ((20496, 20904), (0, 6)), (408, 6)), ((2, -2), (890497, 891937), (6, 3, 2, 2, 2, 10), ((20904, 21144), (0, 6)), (240, 6)), ((2, -2), (897121, 898417), (6, 2, 2, 3, 3, 6), ((19272, 19488), (6, 12)), (216, 6)), ((2, -2), (898417, 899857), (6, 2, 2, 3, 2, 10), ((19488, 19728), (6, 12)), (240, 6)), ((2, -2), (899857, 902305), (6, 2, 2, 3, 2, 17), ((19728, 20136), (6, 12)), (408, 6)), ((2, -2), (904417, 906577), (6, 2, 2, 3, 3, 10), ((20136, 20496), (6, 12)), (360, 6)), ((2, -2), (906577, 909025), (6, 2, 2, 3, 2, 17), ((20496, 20904), (6, 12)), (408, 6)), ((2, -2), (909025, 910465), (6, 2, 2, 3, 2, 10), ((20904, 21144), (6, 12)), (240, 6)), ((4, -4), (0, 2916), (6, 3, 3, 3, 3, 6), ((0, 324), (0, 9)), (324, 9)), ((4, -4), (78804, 86904), (10, 3, 3, 3, 3, 10), ((324, 1224), (0, 9)), (900, 9)), ((4, -4), (86904, 90144), (10, 3, 3, 3, 2, 6), ((1224, 1584), (0, 9)), (360, 9)), ((4, -4), (120204, 123444), (10, 3, 2, 3, 3, 6), ((1584, 1944), (0, 9)), (360, 9)), ((4, -4), (271104, 294513), (17, 3, 3, 3, 3, 17), ((1944, 4545), (0, 9)), (2601, 9)), ((4, -4), (294513, 303693), (17, 3, 3, 3, 2, 10), ((4545, 5565), (0, 9)), (1020, 9)), ((4, -4), (303693, 309201), (17, 3, 3, 3, 2, 6), ((5565, 6177), (0, 9)), (612, 9)), ((4, -4), (356937, 366117), (17, 3, 2, 3, 3, 10), ((6177, 7197), (0, 9)), (1020, 9)), ((4, -4), (366117, 369789), (17, 3, 2, 3, 2, 6), ((7197, 7605), (0, 9)), (408, 9)), ((4, -4), (403857, 409365), (17, 3, 2, 3, 3, 6), ((7605, 8217), (0, 9)), (612, 9)), ((4, -4), (651649, 659749), (10, 3, 3, 3, 3, 10), ((8217, 9117), (0, 9)), (900, 9)), ((4, -4), (659749, 668929), (10, 3, 3, 3, 2, 17), ((9117, 10137), (0, 9)), (1020, 9)), ((4, -4), (668929, 674329), (10, 3, 3, 3, 2, 10), ((10137, 10737), (0, 9)), (600, 9)), ((4, -4), (693049, 702229), (10, 3, 2, 3, 3, 17), ((10737, 11757), (0, 9)), (1020, 9)), ((4, -4), (702229, 705829), (10, 3, 2, 3, 2, 10), ((11757, 12157), (0, 9)), (400, 9)), ((4, -4), (705829, 707989), (10, 3, 2, 3, 2, 6), ((12157, 12397), (0, 9)), (240, 9)), ((4, -4), (726709, 732109), (10, 3, 2, 3, 3, 10), ((12397, 12997), (0, 9)), (600, 9)), ((4, -4), (732109, 734269), (10, 3, 2, 3, 2, 6), ((12997, 13237), (0, 9)), (240, 9)), ((4, -4), (843949, 846865), (6, 3, 3, 3, 3, 6), ((13237, 13561), (0, 9)), (324, 9)), ((4, -4), (846865, 850105), (6, 3, 3, 3, 2, 10), ((13561, 13921), (0, 9)), (360, 9)), ((4, -4), (850105, 855613), (6, 3, 3, 3, 2, 17), ((13921, 14533), (0, 9)), (612, 9)), ((4, -4), (860365, 863605), (6, 3, 2, 3, 3, 10), ((14533, 14893), (0, 9)), (360, 9)), ((4, -4), (863605, 867277), (6, 3, 2, 3, 2, 17), ((14893, 15301), (0, 9)), (408, 9)), ((4, -4), (867277, 869437), (6, 3, 2, 3, 2, 10), ((15301, 15541), (0, 9)), (240, 9)), ((4, -4), (876925, 882433), (6, 3, 2, 3, 3, 17), ((15541, 16153), (0, 9)), (612, 9)), ((4, -4), (882433, 884593), (6, 3, 2, 3, 2, 10), ((16153, 16393), (0, 9)), (240, 9)), ((4, -4), (884593, 885889), (6, 3, 2, 3, 2, 6), ((16393, 16537), (0, 9)), (144, 9)))
a_Dsize=954145

# a_data_size = 1
# a_order = (2, 0, 1)
# a_meta_new = (((1, -1), (1, 1), (0, 1)),)
# a_meta_mrg = (((1, -1), (0, 1), (1, 1, 1), ((0, 1), (0, 1)), (1, 1)),)
# a_Dsize = 1

# a_data_size = 168
# a_order = (1, 0, 2, 3, 4)
# a_meta_new = (((0, 2, 0, 2, 0, 0), (1, 3, 6), (0, 18)), ((0, 4, 0, 2, 0, 2), (2, 3, 9), (18, 72)), ((1, 2, 0, 2, 1, 0), (2, 3, 4), (72, 96)), ((1, 4, 0, 2, 1, 2), (4, 3, 6), (96, 168)))
# a_meta_mrg = (((0, 2, 0, 2, 0, 0), (0, 18), (1, 1, 3, 6, 1), ((0, 1), (0, 3), (0, 6)), (1, 3, 6)), ((0, 4, 0, 2, 0, 2), (18, 72), (1, 2, 3, 9, 1), ((0, 2), (0, 3), (0, 9)), (2, 3, 9)), ((1, 2, 0, 2, 1, 0), (72, 96), (1, 2, 3, 4, 1), ((0, 2), (0, 3), (0, 4)), (2, 3, 4)), ((1, 4, 0, 2, 1, 2), (96, 168), (1, 4, 3, 6, 1), ((0, 4), (0, 3), (0, 6)), (4, 3, 6)))
# a_Dsize = 168

b_data_size= 1048
b_order=(2, 1, 0, 3, 4)
b_meta_new= (((-4, 3), (9, 12), (0, 108)), ((-2, 1), (12, 24), (108, 396)), ((0, -1), (16, 28), (396, 844)), ((2, -3), (8, 21), (844, 1012)), ((4, -5), (4, 9), (1012, 1048)))
b_meta_mrg= (((-4, 3), (0, 36), (1, 3, 3, 2, 2), ((0, 9), (0, 4)), (9, 4)), ((-4, 3), (520, 556), (1, 3, 3, 2, 2), ((0, 9), (4, 8)), (9, 4)), ((-4, 3), (556, 592), (1, 3, 3, 2, 2), ((0, 9), (8, 12)), (9, 4)), ((-2, 1), (36, 60), (1, 3, 2, 2, 2), ((6, 12), (0, 4)), (6, 4)), ((-2, 1), (60, 84), (1, 3, 2, 2, 2), ((6, 12), (4, 8)), (6, 4)), ((-2, 1), (180, 204), (1, 2, 3, 2, 2), ((0, 6), (0, 4)), (6, 4)), ((-2, 1), (204, 228), (1, 2, 3, 2, 2), ((0, 6), (4, 8)), (6, 4)), ((-2, 1), (592, 628), (1, 3, 2, 2, 3), ((6, 12), (8, 14)), (6, 6)), ((-2, 1), (628, 652), (1, 3, 2, 2, 2), ((6, 12), (14, 18)), (6, 4)), ((-2, 1), (652, 688), (1, 3, 2, 3, 2), ((6, 12), (18, 24)), (6, 6)), ((-2, 1), (760, 796), (1, 2, 3, 2, 3), ((0, 6), (8, 14)), (6, 6)), ((-2, 1), (796, 820), (1, 2, 3, 2, 2), ((0, 6), (14, 18)), (6, 4)), ((-2, 1), (820, 856), (1, 2, 3, 3, 2), ((0, 6), (18, 24)), (6, 6)), ((0, -1), (84, 120), (1, 3, 2, 2, 3), ((10, 16), (0, 6)), (6, 6)), ((0, -1), (120, 144), (1, 3, 2, 2, 2), ((10, 16), (6, 10)), (6, 4)), ((0, -1), (144, 180), (1, 3, 2, 3, 2), ((10, 16), (10, 16)), (6, 6)), ((0, -1), (228, 252), (1, 2, 2, 2, 3), ((6, 10), (0, 6)), (4, 6)), ((0, -1), (252, 268), (1, 2, 2, 2, 2), ((6, 10), (6, 10)), (4, 4)), ((0, -1), (268, 292), (1, 2, 2, 3, 2), ((6, 10), (10, 16)), (4, 6)), ((0, -1), (340, 376), (1, 2, 3, 2, 3), ((0, 6), (0, 6)), (6, 6)), ((0, -1), (376, 400), (1, 2, 3, 2, 2), ((0, 6), (6, 10)), (6, 4)), ((0, -1), (400, 436), (1, 2, 3, 3, 2), ((0, 6), (10, 16)), (6, 6)), ((0, -1), (688, 724), (1, 3, 2, 2, 3), ((10, 16), (16, 22)), (6, 6)), ((0, -1), (724, 760), (1, 3, 2, 3, 2), ((10, 16), (22, 28)), (6, 6)), ((0, -1), (856, 880), (1, 2, 2, 2, 3), ((6, 10), (16, 22)), (4, 6)), ((0, -1), (880, 904), (1, 2, 2, 3, 2), ((6, 10), (22, 28)), (4, 6)), ((0, -1), (940, 976), (1, 2, 3, 2, 3), ((0, 6), (16, 22)), (6, 6)), ((0, -1), (976, 1012), (1, 2, 3, 3, 2), ((0, 6), (22, 28)), (6, 6)), ((2, -3), (292, 316), (1, 2, 2, 2, 3), ((4, 8), (0, 6)), (4, 6)), ((2, -3), (316, 340), (1, 2, 2, 3, 2), ((4, 8), (6, 12)), (4, 6)), ((2, -3), (436, 460), (1, 2, 2, 2, 3), ((0, 4), (0, 6)), (4, 6)), ((2, -3), (460, 484), (1, 2, 2, 3, 2), ((0, 4), (6, 12)), (4, 6)), ((2, -3), (904, 940), (1, 2, 2, 3, 3), ((4, 8), (12, 21)), (4, 9)), ((2, -3), (1012, 1048), (1, 2, 2, 3, 3), ((0, 4), (12, 21)), (4, 9)), ((4, -5), (484, 520), (1, 2, 2, 3, 3), ((0, 4), (0, 9)), (4, 9)))
b_Dsize= 1048

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-backend", type=str, choices=['np', 'np-mp', 'torch', 'torch-mp', 'torch-cpp'], default='np')
    parser.add_argument("-device", type=str, default='cpu')
    parser.add_argument("-niter", type=int, default=1000)
    parser.add_argument("-num_threads", type=int, default=-1)
    args = parser.parse_args()

    if args.backend == 'np':
        import backend_np_1d as backend
    elif args.backend == 'torch':
        import backend_torch_1d as backend
        if args.num_threads>0:
            backend.set_num_threads(args.num_threads)
    elif args.backend == 'torch-cpp':
        import backend_torch_cpp_1d as backend

    data_a = backend.randR(a_data_size, args.device)
    data_b = backend.randR(b_data_size, args.device)

    if args.backend=='torch':
        # time computation of source_to_dest map
        # keep_time = time.time()
        # for _ in range(args.niter):
        #     source_to_dest= backend._source_to_dest_v1(data_a, a_order, a_meta_new, a_meta_mrg)
        # print('(_source_to_dest_v1) Total time : %.2f seconds' % (time.time() - keep_time))

        # keep_time = time.time()
        # for _ in range(args.niter):
        #     source_to_dest= backend._source_to_dest_v2(data_a, a_order, a_meta_new, a_meta_mrg)
        # print('(_source_to_dest_v2) Total time : %.2f seconds' % (time.time() - keep_time))

        keep_time = time.time()
        for _ in range(args.niter):
            source_to_dest= backend._source_to_dest_np(data_a, a_order, a_meta_new, a_meta_mrg)
        print('(_source_to_dest_np) Total time : %.2f seconds' % (time.time() - keep_time))

        keep_time = time.time()
        for _ in range(args.niter):
            backend.transpose_and_merge_ptp(data_a, a_order, a_meta_new, a_meta_mrg, a_Dsize)
        print('(transpose_and_merge_ptp) Total time : %.2f seconds' % (time.time() - keep_time))

    if args.backend=='torch-cpp':
        keep_time = time.time()
        for _ in range(args.niter):
            source_to_dest= backend._source_to_dest_plain(data_a, a_order, a_meta_new, a_meta_mrg)
        print('(_source_to_dest_plain) Total time : %.2f seconds' % (time.time() - keep_time))

        keep_time = time.time()
        for _ in range(args.niter):
            source_to_dest= backend._source_to_dest_plain_omp(data_a, a_order, a_meta_new, a_meta_mrg)
        print('(_source_to_dest_plain_omp) Total time : %.2f seconds' % (time.time() - keep_time))

        keep_time = time.time()
        for _ in range(args.niter):
            source_to_dest= backend._source_to_dest_plain_omp_v2(data_a, a_order, a_meta_new, a_meta_mrg)
        print('(_source_to_dest_plain_omp_v2) Total time : %.2f seconds' % (time.time() - keep_time))

        keep_time = time.time()
        for _ in range(args.niter):
            source_to_dest= backend._source_to_dest_plain_omp_v2(data_a, a_order, a_meta_new, a_meta_mrg)
        print('(_source_to_dest_plain_omp_v3) Total time : %.2f seconds' % (time.time() - keep_time))

        keep_time = time.time()
        for _ in range(args.niter):
            backend.transpose_and_merge_ptp(data_a, a_order, a_meta_new, a_meta_mrg, a_Dsize)
        print('(transpose_and_merge_ptp) Total time : %.2f seconds' % (time.time() - keep_time))

        keep_time = time.time()
        for _ in range(args.niter):
            backend.transpose_and_merge_omp(data_a, a_order, a_meta_new, a_meta_mrg, a_Dsize)
        print('(transpose_and_merge_omp) Total time : %.2f seconds' % (time.time() - keep_time))

        keep_time = time.time()
        for _ in range(args.niter):
            backend.transpose_and_merge_ptp_omp(data_a, a_order, a_meta_new, a_meta_mrg, a_Dsize)
        print('(transpose_and_merge_ptp_omp) Total time : %.2f seconds' % (time.time() - keep_time))

        keep_time = time.time()
        for _ in range(args.niter):
            backend.transpose_and_merge_ptp_omp_v2(data_a, a_order, a_meta_new, a_meta_mrg, a_Dsize)
        print('(transpose_and_merge_ptp_omp_v2) Total time : %.2f seconds' % (time.time() - keep_time))

    keep_time = time.time()
    for _ in range(args.niter):
        backend.transpose_and_merge(data_a, a_order, a_meta_new, a_meta_mrg, a_Dsize)

    print('Total time : %.2f seconds' % (time.time() - keep_time))

    # verify
    if not args.backend=='np':
        import numpy as np
        import backend_np_1d as backend_np
        res_ref= backend_np.transpose_and_merge(data_a.numpy(), a_order, a_meta_new, a_meta_mrg, a_Dsize)
        res_0= backend.transpose_and_merge(data_a, a_order, a_meta_new, a_meta_mrg, a_Dsize)
        res_ptp= backend.transpose_and_merge_ptp(data_a, a_order, a_meta_new, a_meta_mrg, a_Dsize)
        res_ptp_v2= backend.transpose_and_merge_ptp_omp_v2(data_a, a_order, a_meta_new, a_meta_mrg, a_Dsize)
        print(f"Verify (transpose_and_merge) {np.linalg.norm(res_ref-res_0.numpy())}")
        print(f"Verify (transpose_and_merge_ptp) {np.linalg.norm(res_ref-res_ptp.numpy())}")
        print(f"Verify (transpose_and_merge_ptp_omp_v2) {np.linalg.norm(res_ref-res_ptp_v2.numpy())}")
        import pdb; pdb.set_trace();
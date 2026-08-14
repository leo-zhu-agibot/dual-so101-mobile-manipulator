.PHONY: test model build

test:
	PYTHONPATH=data_pipeline/src pytest

model:
	xacro robot_ws/src/dual_so101_description/urdf/dual_so101_mobile.urdf.xacro use_mock_hardware:=true -o /tmp/dual_so101_mobile.urdf

build:
	cd robot_ws && colcon build --symlink-install


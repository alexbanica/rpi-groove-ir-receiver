from pathlib import Path

from setuptools import find_packages, setup


INSTALL_REQUIRES = [
    'pigpio>=1.78',
    'spidev>=3.6; platform_system == "Linux"',
    'RPi.GPIO>=0.7.1; platform_system == "Linux" and (platform_machine == "armv7l" or platform_machine == "armv6l")',
    'Hobot.GPIO>=0.1.0; platform_system == "Linux" and platform_machine == "aarch64"',
    'Jetson.GPIO>=2.1.0; platform_system == "Linux" and platform_machine == "aarch64"',
]

README_CONTENT = Path("README.md").read_text(encoding="utf-8")

setup(
    name="rpi-groove-ir-receiver",
    version="1.1.0",
    description="Raspberry Pi Grove IR receiver utilities",
    long_description=README_CONTENT,
    long_description_content_type="text/markdown",
    author="Alex Banica",
    author_email="ionut.alexandru.banica@gmail.com",
    python_requires=">=3.9",
    packages=find_packages(exclude=("tests", "tests.*")),
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Operating System :: POSIX :: Linux",
    ],
)

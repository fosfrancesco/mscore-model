import setuptools

setuptools.setup(
    name="score_model",
    version="0.0.1",
    description="Classes and functions to model a musical score.",
    author="Francesco Foscarin",
    author_email="foscarin.francesco@gmail.com",
    url="https://gitlab.com/fosfrancesco/score_model",
    packages=setuptools.find_packages(),
    long_description="""
    Classes and functions to model a musical score.
    Model the engraving layer with sequential and tree structures.
    """,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Musical Score",
    ],
    keywords="music musical score",
    license="MIT",
    python_requires=">=3.6",
)


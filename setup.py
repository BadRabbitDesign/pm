from setuptools import setup, find_packages


_entry_points = {
    "gui_scripts": [],
    "console_scripts": [],
}


setup(
    name="pm2000",
    version="0.0.0",
    description="Tools for LUCY",
    author="Caspar Lucas",
    author_email="casparlucas@hotmail.co.uk",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        "flask>=3",   
        "Flask-WTF",
        "flask-debugtoolbar",
        "flask-nav",
        "flask-login",
        "flask-mail",
        "flask-cors",
        "MarkupSafe==2.1.1",
        "jinja2>=3.1.2",
        "sqlalchemy",
        "bcrypt",
    ],
    package_data={},
    entry_points=_entry_points,
)

History = """

"""

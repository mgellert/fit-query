from click.testing import CliRunner

from src.fit_query.console import cli


def test_import():
    runner = CliRunner(env={'TEST': '1'})
    result = runner.invoke(cli, ['import', './files/'])
    print(result.output)

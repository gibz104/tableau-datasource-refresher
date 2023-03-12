from unittest.mock import patch, call, Mock
from tableau_datasource_refresher.tableau import TableauPublic


def test_tableau_init():
    # Test default parameters
    with patch('tableau_datasource_refresher.tableau.os') as mock_os:
        mock_os.getenv.side_effect = ['test@test.com', 'testpassword']
        example_tableau = TableauPublic()

        mock_os.getenv.assert_has_calls([call('TABLEAU_USER'), call('TABLEAU_PASS')])
        assert example_tableau.username == 'test@test.com'
        assert example_tableau.password == 'testpassword'
        assert example_tableau.server_url == 'https://public.tableau.com'
        assert example_tableau.headless is False

    # Test custom parameters
    with patch('tableau_datasource_refresher.tableau.os'):
        example_tableau = TableauPublic(
            username='test2@test.com',
            password='testpassword2',
            server_url='https://test.tableau.com',
            headless=True,
        )

        assert example_tableau.username == 'test2@test.com'
        assert example_tableau.password == 'testpassword2'
        assert example_tableau.server_url == 'https://test.tableau.com'
        assert example_tableau.headless is True


def test_base_url():
    with patch('tableau_datasource_refresher.tableau.os'):
        example_tableau = TableauPublic(
            server_url='https://test.tableau.com/',
        )
        url = example_tableau.base_url
        assert url == 'https://test.tableau.com'

    with patch('tableau_datasource_refresher.tableau.os'):
        example_tableau = TableauPublic(
            server_url='https://test.tableau.com',
        )
        url = example_tableau.base_url
        assert url == 'https://test.tableau.com'


@patch('tableau_datasource_refresher.tableau.ChromeDriverManager')
@patch('tableau_datasource_refresher.tableau.ChromeService')
@patch('tableau_datasource_refresher.tableau.webdriver.Chrome')
@patch('tableau_datasource_refresher.tableau.webdriver.ChromeOptions')
@patch('tableau_datasource_refresher.tableau.stealth')
def test_browser(mock_stealth, mock_chromeoptions, mock_chrome, mock_chromeservice, mock_chromedrivermanager):
    example_tableau = TableauPublic()
    driver = example_tableau.browser

    # Test adding options to browser
    calls = [
        call("--window-size=1920,1080"),
        call("start-maximized"),
    ]
    mock_chromeoptions().add_argument.assert_has_calls(calls)
    calls = [
        call("excludeSwitches", ["enable-automation"]),
        call('useAutomationExtension', False),
        call(
            "prefs",
            {
             "credentials_enable_service": False,
             "profile.password_manager_enabled": False,
            },
        )
    ]
    mock_chromeoptions().add_experimental_option.assert_has_calls(calls)

    # Test creating Chrome driver
    mock_chrome.assert_called_once_with(
        options=mock_chromeoptions(),
        service=mock_chromeservice(mock_chromedrivermanager().install)
    )

    # Test stealth was called
    mock_stealth.assert_called_once()

    assert driver is mock_chrome()


@patch('tableau_datasource_refresher.tableau.TableauPublic.browser')
def test_check_stealth(mock_browser):
    # Test to make sure stealth is called
    example_tableau = TableauPublic()
    example_tableau.check_stealth()
    mock_browser.get().called_once_with('https://pixelscan.net/')


@patch('tableau_datasource_refresher.tableau.WebDriverWait')
@patch('tableau_datasource_refresher.tableau.TableauPublic.browser')
def test_signin(mock_browser, mock_webdriverwait):
    # Test to make sure correct browser actions are called
    with patch('tableau_datasource_refresher.tableau.time'):
        example_tableau = TableauPublic(
            username='test2@test.com',
            password='testpassword2',
            server_url='https://test.tableau.com/',
        )
        example_tableau.signin()
        mock_browser.get().called_once_with('https://test.tableau.com/app/discover?authMode=signIn')

        calls = [
            call('test2@test.com'),
            call('testpassword2'),
        ]
        mock_webdriverwait().until().send_keys.assert_has_calls(calls)
        mock_webdriverwait().until().click.assert_called_once()


@patch('tableau_datasource_refresher.tableau.WebDriverWait')
@patch('tableau_datasource_refresher.tableau.TableauPublic.browser')
def test_signout(mock_browser, mock_webdriverwait):
    # Test to make sure correct browser actions are called
    with patch('tableau_datasource_refresher.tableau.time'):
        example_tableau = TableauPublic(
            server_url='https://test.tableau.com/',
        )
        example_tableau.signout()
        mock_browser.get().called_once_with('https://test.tableau.com/app/discover')

        assert mock_webdriverwait().until().click.call_count == 2
        mock_browser.close.assert_called_once()


@patch('tableau_datasource_refresher.tableau.WebDriverWait')
@patch('tableau_datasource_refresher.tableau.TableauPublic.browser')
def test_refresh_datasource(mock_browser, mock_webdriverwait):
    # Test to make sure correct browser actions are called
    with patch('tableau_datasource_refresher.tableau.time'):
        example_tableau = TableauPublic(
            server_url='https://test.tableau.com/',
        )
        example_tableau.refresh_datasource('/viz/TestViz/Home')
        mock_browser.get().called_once_with('https://test.tableau.com/viz/TestViz/Home')

        mock_webdriverwait().until().click.assert_called_once()


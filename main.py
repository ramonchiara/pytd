from bs4 import BeautifulSoup
from dotenv import dotenv_values
import json
import requests


class TesouroDireto:
    _base_url = 'https://portalinvestidor.tesourodireto.com.br'

    def __init__(self):
        self._logged = False

    def login(self, cpf, senha):
        self._get_initial_page()
        self._send_cpf(cpf)
        self._send_senha(cpf, senha)
        return self._logged

    def _get_initial_page(self):
        url = TesouroDireto._base_url
        response = requests.get(url)
        assert response.status_code == 200
        assert response.text.find('name="UserCpf"') != -1
        self._cookies = response.cookies
        self._token = TesouroDireto._extract_verification_token(response)

    @staticmethod
    def _extract_verification_token(response):
        soup = BeautifulSoup(response.text, 'html.parser')
        token = soup.find('input', {'name': '__RequestVerificationToken'}).get('value')
        return token

    def _send_cpf(self, cpf):
        url = TesouroDireto._base_url + '/login/deve-exibir-captcha'
        data = {'UserCpf': cpf, '__RequestVerificationToken': self._token}
        response = requests.post(url, cookies=self._cookies, data=data)
        assert response.status_code == 200
        response_values = json.loads(response.text)
        assert response_values.get('Success')
        assert response_values.get('ErrorMessage') is None
        assert not response_values.get('MustShowCaptcha')

    def _send_senha(self, cpf, senha):
        url = TesouroDireto._base_url + '/Login/validateLogin'
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        data = {'UserCpf': cpf, 'UserPassword': senha, '__RequestVerificationToken': self._token}
        response = requests.post(url, cookies=self._cookies, headers=headers, data=data)
        assert response.status_code == 200
        self._cookies = response.cookies
        self._logged = True

    def get_titulos_investidos(self):
        self._verify_logged()
        url = TesouroDireto._base_url + '/MeusInvestimentos'
        response = requests.get(url, cookies=self._cookies)
        assert response.status_code == 200
        assert response.text.find('id="usuario"') != -1
        assert response.text.find('action="/Login/Logout"') != -1
        soup = BeautifulSoup(response.text, 'html.parser')
        table_container = soup.find(id='table-container_1')
        titulos = self._extract_titulos(table_container)
        return titulos

    def _extract_titulos(self, table_container):
        titulos = []
        links = table_container.find_all('a')
        for link in links:
            url_titulo = link.get('href')
            url = TesouroDireto._base_url + url_titulo
            response = requests.get(url, cookies=self._cookies)
            assert response.status_code == 200
            soup = BeautifulSoup(response.text, 'html.parser')
            nome = soup.find('h1', {'class': 'td-meus-investimentos-detalhe__titulo_card'}).text.strip()
            vencimento = soup.select('tr.saldo-table-vencimento th strong')[0].text[-10:]
            instituicao = soup.find('span', {'class': 'td-meus-investimentos-deatlhe-instituicao__nome'}).text.strip()
            linhas = soup.find_all('tr', {'class': 'saldo-table-data-values'})
            for linha in linhas:
                tds = linha.find_all('td')
                titulo = {
                    'nome': nome,
                    'vencimento': vencimento,
                    'instituicao': instituicao,
                    'data_aplicacao': tds[1].text.strip(),
                    'quantidade_titulos': tds[2].text.strip(),
                    'preco_titulo_aplicacao': tds[3].text.strip(),
                    'valor_investido': tds[4].text.strip(),
                    'rentabilidade_contratada': tds[5].text.strip(),
                    'rentabilidade_acumulada_anualizada': tds[6].text.strip(),
                    'rentabilidade_acumulada': tds[7].text.strip(),
                    'valor_bruto': tds[8].text.strip(),
                    'dias_aplicados': tds[9].text.strip(),
                    'aliquota_ir': tds[10].text.strip(),
                    'valor_imposto_ir': tds[11].text.strip(),
                    'valor_imposto_iof': tds[12].text.strip(),
                    'valor_taxa_b3': tds[13].text.strip(),
                    'valor_taxa_instituicao': tds[14].text.strip(),
                    'valor_liquido': tds[15].text.strip()
                }
                titulos.append(titulo)
        return titulos

    def logout(self):
        self._verify_logged()
        url = TesouroDireto._base_url + '/Login/Logout'
        response = requests.post(url, cookies=self._cookies, allow_redirects=False)
        assert response.status_code == 302
        assert response.headers.get('Location') == '/'
        del self._cookies
        self._logged = False

    def _verify_logged(self):
        if not self._logged:
            raise RuntimeError('Você não está logado!')


if __name__ == '__main__':
    config = dotenv_values(".env")
    cpf = config['CPF']
    senha = config['SENHA']

    td = TesouroDireto()
    res = td.login(cpf, senha)
    titulos = td.get_titulos_investidos()
    for titulo in titulos:
        print(titulo)
    td.logout()

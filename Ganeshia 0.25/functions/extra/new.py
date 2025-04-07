from bs4 import BeautifulSoup

def news(response):
    if response.status_code == 200:
    # Passo 4: Fazer o parsing do conteúdo HTML
        soup = BeautifulSoup(response.content, 'html.parser')

    # Passo 5: Encontrar e extrair o título da página
        titulo = soup.find('h1').get_text()
        
    else:
        print('Erro ao acessar a página:', response.status_code)
    
    return titulo
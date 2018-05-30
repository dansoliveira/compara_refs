from os import listdir
from os.path import isfile, join
from numpy import zeros
from math import sqrt
import timeit

# Stopwords coletadas em https://github.com/stopwords-iso/stopwords-en
path = "referencias"
stopwords = set(word.replace("\n", "") for word in open("stopwords.txt", "r", encoding="utf8"))
bagOfWords = [[]]
palavras = []  # Representa as colunas da bagOfWords. Armazena, unicamente, todas as palavras encontradas
'''hashArtigoNumRef - Representa as linhas da bagOfWords. É uma representação única de cada referência, composta por 
"nomeDoArquivo.txt[NUMREF]", onde o [NUMREF] equivale ao número da referência no arquivo
'''
hashArtigoNumRef = []

class IEEE(object):
    referencias = {}  # key: número da ref.; value: list com a ref. tratada (removido stopwords, pontos, virgulas, aspas)
    artigoReferencias = {}  # key: nome; value: referencias;

    def load_refs(self):
        """Método responsável por carregar as referências obtidas dos artigos da IEEE.
        """
        arquivos = [f for f in listdir(path) if isfile(join(path, f))]
        for arq in arquivos: # Para cada artigo...
            arqaberto = open(join(path, arq), encoding='latin-1')

            for linha in arqaberto:  # Para cada linha do artigo...
                linha = linha.strip()  # Garante que linhas totalmente em branco serão ignoradas
                if linha:
                    num = self.get_num(linha)
                    ref = self.get_ref(linha)
                    newRef = self.limpa_linha(ref)
                    newRef = self.remove_stopwords(newRef)

                    self.referencias.__setitem__(num, newRef)

            arqaberto.close()
            self.artigoReferencias.__setitem__(arq, self.referencias)
            self.referencias = {}

    def get_num(self, linha: str):
        """Coleta a numeração da referência no artigo
        """
        num = linha[:3].replace(" ", "")
        num = num.replace(".", "")
        return num

    def get_ref(self, linha: str):
        """Coleta a referência sem a numeração
        """
        return linha[3:].strip()

    def remove_stopwords(self, referencia: str):
        """Método responsável por remover as stopwords da referência.
           Args:
               referencia - str com a referência a ser removida

           Returns:
               list com a nova referência sem as stopwords

        """
        linha_atualizada = []

        for word in referencia.split(" "):
            if word not in stopwords:
                linha_atualizada.append(word)
                if word not in palavras:  # Se a palavra ainda não foi encontrada, adiciona na lista das encontradas
                    palavras.append(word)

        return linha_atualizada

    def limpa_linha(self, linha: str):
        """Remove caracteres que possam atrapalhar a coleta e comparação de palavras.
        Os caracteres removidos são:
        - . (ponto), " (aspas) e , (vírgula)
            Args:
                linha - str contendo a linha a ser limpa

            Returns:
                str da linha limpa
        """
        linhaAtualizada = linha.replace(".", "")
        linhaAtualizada = linhaAtualizada.replace("\"", "")
        linhaAtualizada = linhaAtualizada.replace(",", "")

        return linhaAtualizada


def similaridade(artNum1: str, artNum2: str):
    """Método responsável por comparar a similaridade entre 2 artigos. O método utilizdo é o Bag of Words Binário
       Args:
           nomeArtigo1 - str
           nomeArtigo2 - str

        Returns:
            float representando o resultado da comparação
    """

    indiceA1 = hashArtigoNumRef.index(artNum1)
    indiceA2 = hashArtigoNumRef.index(artNum2)

    sumSup = 0
    sumInfA1 = 0
    sumInfA2 = 0

    for i in range(palavras.__len__()):
        valorA1 = bagOfWords[indiceA1][i]
        valorA2 = bagOfWords[indiceA2][i]
        produtoA1A2 = valorA1 * valorA2

        sumSup += produtoA1A2
        sumInfA1 += valorA1 ** 2
        sumInfA2 += valorA2 ** 2

    sumInfTotal = sqrt(sumInfA1) * sqrt(sumInfA2)

    return sumSup / sumInfTotal

def preenche_bag_of_words():
    """Preenche a matriz da Bag of Words de acordo com as regras da técnica.
    """
    for artigo in artigoReferencias.keys():
        referencias = artigoReferencias.get(artigo)
        for num, referencia in referencias.items():
            for palavra in referencia:
                indicePalavra = palavras.index(palavra)
                indiceArtigo = hashArtigoNumRef.index(artigo + num)

                bagOfWords[indiceArtigo][indicePalavra] = 1

def inicia_bag_of_words():
    """Inicia a matriz da Bag of Words com zeros, onde as linhas representam cada referência de cada artigo, e as
    colunas são todas as palavras encontradas (sem repetição).

        Returns:
            matriz de zeros com tamanho de acordo com a quantidade de referências e de palavras encontradas
    """
    # Coleta a quantidade total de referências
    qtdReferenciasTotal = 0
    for artigo in artigoReferencias.keys():
        referencias = artigoReferencias.get(artigo)
        qtdReferenciasTotal += referencias.__len__()
        for num, ref in referencias.items():
            hashArtigoNumRef.append(artigo + num)

    return zeros((qtdReferenciasTotal, palavras.__len__()))

if __name__ == "__main__":
    sim = {}

    ieeeRefs = IEEE()
    ieeeRefs.load_refs()

    bagOfWords = inicia_bag_of_words()
    preenche_bag_of_words()

    artigoReferencias = ieeeRefs.artigoReferencias
    artigos = artigoReferencias.items()

    time1 = timeit.timeit()
    for artigo_1, referencias_1 in artigos:
        for artigo_2, referencias_2 in artigos:
            if artigo_1 != artigo_2:
                for num_1, ref_1 in referencias_1.items():
                    for num_2, ref_2 in referencias_2.items():
                        artNum1 = artigo_1 + num_1
                        artNum2 = artigo_2 + num_2

                        simAN1AN2 = "sim({}, {})".format(artNum1, artNum2)
                        simAN2AN1 = "sim({}, {})".format(artNum2, artNum1)

                        # Se a similaridade sim(A1, A2) ou sim(A2, A1) ainda não foi calculada...
                        if not sim.get(simAN1AN2) and not sim.get(simAN2AN1):
                            sim.__setitem__(simAN1AN2, similaridade(artNum1, artNum2))

    time2 = timeit.timeit()
    print("Tempo de cálculo da BagOfWords: {}".format(time2 - time1))

    cont = 0
    with open("resultadosSim.txt", "w") as arqResultado:
        for nomeSim, valorSim in sim.items():
            linha = "{} -> {}\n".format(nomeSim, valorSim)
            # Salva apenas referências que tenham similaridade maior que 70%
            if valorSim > 0.7:
                cont += 1
                print(linha)
                arqResultado.write(linha)

    arqResultado.close()
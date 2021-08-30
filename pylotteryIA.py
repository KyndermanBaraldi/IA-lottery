import constants as modal
import helpers
import csv
import requests
import pickle
from pybrain3.tools.shortcuts import buildNetwork
from pybrain3.datasets import SupervisedDataSet
from pybrain3.supervised.trainers import BackpropTrainer
from bs4 import BeautifulSoup

class loteryIA:

    def __init__(self, lottery, loadNetwork = False, dowloadResults = True, percent = 0.8, showMessages = True):

        self.__lottery = modal.LOTTERY[lottery]
        self.__OUTPUTS_FILE = self.__lottery['lottery'] + '_outputs.csv'
        self.__INPUTS_FILE = self.__lottery['lottery'] + '_inputs.csv'
        self.__percent = percent
        self.__showMessages = showMessages
        if dowloadResults: self.__downloadResults()

        self.__setOutputs()
        self.__setInputs()

        self.__inputlayer = len(self.__inputs[0])
        self.__hiddenlayer = (round(self.__inputlayer * 2 / 3) + self.__lottery['choice']) + 1
        self.__outputlayer = self.__lottery['raffle']


        if loadNetwork:
            self.__loadNetwork()
        else:
            self.__network = buildNetwork(self.__inputlayer, self.__hiddenlayer, self.__outputlayer, bias=True)
            self.__setSupevisedDataSet()

        self.__trainer = BackpropTrainer(self.__network)

    def __print(self, *values):
        if self.__showMessages:
            print(*values)

    def __downloadResults(self):

        self.__print("- Baixano o arquivo de resultados...")
        self.__print(self.__lottery['URL_results'])
        f = requests.get(self.__lottery['URL_results'])

        self.__print("- Pronto! Convertendo o arquivo de resultados...")


        strHTML = helpers.filterHTMLtable(str(f.content))

        soup = BeautifulSoup(strHTML, 'html5lib')

        self.__print("- Pronto! Extraindo os resultados...")

        col = []
        con = 0
        with open(self.__OUTPUTS_FILE, 'w') as saidas:
            for i, l in enumerate(soup.find_all('tr')):

                if i == 0:
                    for k, s in enumerate(l.find_all('th')):
                        if 'coluna' in str(s.string).lower() or\
                                'bola' in str(s.string).lower() or\
                                    'dezena' in str(s.string).lower():
                            col.append(k)

                else:
                    s = l.find_all('td')
                    if len(s) > col[len(col) - 1]:

                        result = ''
                        con += 1
                        if con > 1:
                            result = '\n'

                        for k in col:
                            result = result + str(int(s[k].string)) + ';'

                        saidas.writelines(result.rstrip(';'))

        self.__print("- finalizado!")


    def __setOutputs(self):

        list = []
        with open(self.__OUTPUTS_FILE) as _file:
            data = csv.reader(_file, delimiter=";")
            for line in data:
                line = [float(elemento.replace(",", ".")) for elemento in line]
                list.append(line)

        self.__outputs = list


    def __setInputs(self):

        list = []
        c = self.__lottery['ticket']
        h = 1
        primary = [0 for l in range(c * 2)]
        list.append(primary)

        with open(self.__INPUTS_FILE, "w+") as _file:
            strlist = str(primary).strip("[").strip("]").replace(",", ";")
            _file.writelines(strlist)
            for res in self.__outputs:
                list.append(list[h - 1])
                for k in range(c):
                    if (k + 1) in res:
                        list[h][(k * 2) + 1] = 0
                        list[h][(k * 2)] = (list[h][(k * 2)] * ((h - 1) * c/100) + 1) / (h * c/100)
                    else:
                        list[h][(k * 2) + 1] += 1
                        list[h][(k * 2)] = (list[h][(k * 2)] * ((h - 1) * c/100)) / (h * c/100)

                strlist = str(list[h]).strip("[").strip("]").replace(",", ";")
                _file.writelines("\n")
                _file.writelines(strlist)
                h += 1

        self.__inputs = list


    def __setSupevisedDataSet(self):

        length = int(len(self.__outputs) * self.__percent)
        start = len(self.__outputs) - length - 1

        self.__sdataset = SupervisedDataSet(self.__inputlayer, self.__outputlayer)

        for l in range(length):
            self.__sdataset.addSample(self.__inputs[start + l], self.__outputs[start + l])

        self.__print(f"Adcionados {length + 1} de {len(self.__outputs)} resultados ({self.__percent * 100}%): concursos {start} a {start + length + 1}.")


    def __loadNetwork(self):

        source = self.__lottery['lottery']

        with open(source + '.dataset', 'rb') as _file:
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            self.__sdataset = pickle.load(_file)

        with open(source + '.network', 'rb') as _file:
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            self.__network = pickle.load(_file)


    def saveNetwork(self):

        source = self.__lottery['lottery']

        with open(source + '.dataset', 'wb') as _file:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(self.__sdataset, _file, pickle.HIGHEST_PROTOCOL)

        with open(source + '.network', 'wb') as _file:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(self.__network, _file, pickle.HIGHEST_PROTOCOL)


    def trainNetwork(self, epochs = 27180):

        self.__print(f"Treinando a rede com {epochs} épocas")

        if epochs > 0:
            for i in range(epochs):
                self.__trainer.trainOnDataset(self.__sdataset)
                self.__print("TREINANDO", "." * (i % 4))
                self.__print(round(i * 100 / epochs, 2), '%')
        else:
            self.__print("Não foi realzado nenhum treinamento.")


    def update(self):

        self.__sdataset.clear()
        self.__downloadResults()
        self.__outputs.clear()
        self.__setOutputs()
        self.__inputs.clear()
        self.__setInputs()
        self.__setSupevisedDataSet()


    def shots(self, q):

        mylist = []

        Fo = 0
        Fa = 1

        while True:

            z = self.__network.activate(self.__inputs[len(self.__inputs) - 1])
            z = [int(round(numero, 0)) for numero in z]

            j = []

            for numero in z:
                if (numero in range(1, self.__lottery['ticket']+1)) and (numero not in j):
                    j.append(numero)

            Fa = Fa + Fo
            Fo = Fa - Fo

            while len(j) < self.__lottery['choice']:

                self.trainNetwork(1)
                z = self.__network.activate(self.__inputs[len(self.__inputs) - 1])
                z = [int(round(numero, 0)) for numero in z]

                for numero in z:
                    if (numero in range(1, self.__lottery['ticket']+1)) and (numero not in j):
                        j.append(numero)
                        if len(j) == self.__lottery['choice']:
                            break

            j.sort()

            if j not in mylist:
                mylist.append(j)
                self.__print(f'{len(mylist)} jogo(s) gerado(s)')

            if len(mylist) < q:
                self.trainNetwork(Fa)
            else: break

        return mylist
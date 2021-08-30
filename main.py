import pylotteryIA
import constants as modal

if __name__ == '__main__':

    mega = pylotteryIA.loteryIA(modal.MEGASENA, loadNetwork=False, dowloadResults=True)
    mega.trainNetwork(1)
    
    while True:

        print("=" * 29)
        print(" " * 10, "Loterias")
        print("=" * 29)
        print("digite 'a' para atualizar")
        print("digite 't' para treinar")
        print("digite 's' para sair")
        q = input("Quantos palpites você deseja?")

        if q == "s":

            while True:
                t = input('deseja salvar? (s/n)')
                if t == 'n': break
                elif t == 's':
                    mega.saveNetwork()
                    break
                else: print("Valor inválido. Digite s ou n.")

            break

        elif q == "t":

            print("Digite 0 (zero) para voltar")
            while True:
                t = input("Quantos épocas você deseja?")
                if t.isdigit(): break
                print("Valor inválido. Digite um numeral.")

            mega.trainNetwork(int(t))

        elif q == "a":

            mega.update()
            print("Estatísticas atualizadas com sucesso.")

        elif q.isdigit():

            print( "*" * 8, f"gerando {q} palpites", "*" * 8)
            print("Abaixo está meu palpite para os próximos sorteios:")
            mylist = mega.shots(int(q))

            with open("palpites.txt", "w+") as arquivo:
                for z1 in mylist:
                    z1 = [str(numero).zfill(2) for numero in z1]
                    str_z = str(z1).strip("[").strip("]").replace("\'", "").replace(",", "")
                    arquivo.writelines(str_z)
                    arquivo.writelines("\n")
                    print(str_z)

            print(">" * 9, "BOA SORTE", "<" * 9)

        else: print("Opção inválida")

    print(">" * 9, "OBRIGADO", "<" * 9)
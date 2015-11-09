import json, krakenex, time, npyscreen, curses

def Evolution():
        try:
                histo = k.query_public('OHLC',{'pair' : 'XBTEUR', 'interval' : 5})['result']['XXBTZEUR']
        except Exception:
                histo = []
        tendance = []
        for date in histo:
                if float(date[5]) != 0:
                        tendance.append(float(date[5]))
        trend = [b - a for a, b in zip(tendance[::1], tendance[1::1])]
        trends = map(str,trend)
        return trends

def refreshOp():
        opaff = []
        operation = k.query_private('OpenPositions',{'docalcs' : 'true'})['result']        
        for op in operation:
            profit = float(operation[op]['value']) - float(operation[op]['fee']) - float(operation[op]['cost']) - float(operation[op]['value']) * float(fraisachat)*0.01
            opaff.append(operation[op]['cost'] + ' euros ' + operation[op]['fee'] + ' euros ' + operation[op]['net'] + ' profit ' + str(profit))
        return opaff
def refreshOrd():
        ordaff = []
        commandes = k.query_private('OpenOrders',{'trades' : 'true'})['result']['open']
        for commande in commandes:
            ordaff.append(commandes[commande]['descr']['order'])
        return ordaff
class Principal(npyscreen.ActionFormMinimal):
    def create(self):
       #self.Name = self.add(npyscreen.TitleSelectOne, scroll_exit=True, max_height=3, name='Name', values = utilisateurs)
       self.Compte = self.add(npyscreen.TitleFixedText, value=comptes, use_two_lines=True,begin_entry_at=0, name='Comptes',editable=False)
       self.Fees = self.add(npyscreen.TitleFixedText, value=fees, use_two_lines=True,begin_entry_at=0, name='Frais',editable=False)
       self.cours = self.add(npyscreen.TitleFixedText, value=cours, use_two_lines=True,begin_entry_at=0, name='Cours',editable=False)
       self.Affichage = self.add(npyscreen.TitlePager, values=opaff, use_two_lines=True,begin_entry_at=0, max_height=11, name='Operations',editable=False)
       self.Affichageord = self.add(npyscreen.TitlePager, values=ordaff, use_two_lines=True,begin_entry_at=0, max_height=11, name='Operations',editable=False)
       self.keypress_timeout = 20
    def while_waiting(self):
       reponse = k.query_public('Ticker',{'pair' : 'XBTEUR'})['result']['XXBTZEUR']
       trending = Evolution()
       if len(trending) > 1:
        cours = reponse['c'][0]+ " " + trending[len(trending)-1] + " " + trending[len(trending)-2] + " " + trending[len(trending)-3]
       else:
        cours = reponse['c'][0]
       self.cours.value = cours
       self.cours.display()
       self.Affichage.values = refreshOp()
       self.Affichage.display()
       self.Affichageord.values = refreshOrd()
       #self.Affichageord.values = Evolution()
       self.Affichageord.display()
class KrakenApp(npyscreen.NPSAppManaged):
   def onStart(self):
       self.addForm('MAIN', Principal, name='Gestion de Kraken')
   def onInMainLoop(self):
       pass

if __name__ == "__main__":
    with open("user.json","r") as data_file:
        user = json.load(data_file)
    k = krakenex.API()
    k.load_key('kraken.key')
    comptes = "test"
    i = 0
    reponse = k.query_public('AssetPairs',{'pair' : 'XBTEUR'})
    balance = k.query_private('Balance')['result']
    comptes = balance['ZEUR'] + ' euros ' + balance['XXBT'] + ' btc ' + balance['XLTC'] + ' ltc'
    frais = k.query_private('TradeVolume',{'pair' : 'XBTEUR'})['result']
    fraisachat =  frais['fees_maker']['XXBTZEUR']['fee']
    fraisvente = frais['fees']['XXBTZEUR']['fee']
    fees = fraisachat + " " + fraisvente
    operation = k.query_private('OpenPositions',{'docalcs' : 'true'})['result']
    opaff = []
    ordaff = []
    for op in operation:
        profit = float(operation[op]['value']) - float(operation[op]['fee']) - float(operation[op]['cost']) - float(operation[op]['value']) * float(fraisachat)*0.01
        opaff.append(operation[op]['cost'] + ' euros ' + operation[op]['fee'] + ' euros ' + operation[op]['net'] + ' profit ' + str(profit))
    commandes = k.query_private('OpenOrders',{'trades' : 'true'})['result']['open']
    for commande in commandes:
        ordaff.append(commandes[commande]['descr']['order'])
    reponse = k.query_public('Ticker',{'pair' : 'XBTEUR'})['result']['XXBTZEUR']
    cours = reponse['c'][0]    
    App = KrakenApp().run()
while True:
        reponse = k.query_public('Ticker',{'pair' : 'XBTEUR'})['result']['XXBTZEUR']
        print reponse['c'][0]
        time.sleep(1)

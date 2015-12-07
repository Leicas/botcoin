import json, krakenex, time, npyscreen, curses
import numpy as np
from scipy import stats
commandesbot = {}
iteration = 0
itermax = 3

def EnProfit(cours, fee):
    global commandesbot
    commandes = {}
    for commande in commandesbot:
      profit = float(commandesbot[commande]['vol']) * float(cours)
      profit = profit - profit * float(fee) * 0.01
      profit = profit - float( commandesbot[commande]['cost']) - float(commandesbot[commande]['fee'])
      if profit > 0.05:
        commandes[commande] = commandesbot[commande]
    return commandes
def refreshbotOrd(user, cours, fee):
    global commandesbot
    botord = []
    botorder = {}
    retouran = {}
    for botcom in user['Order']:
      if botcom[0] in commandesbot:
        botorder[botcom[0]] = commandesbot[botcom[0]]
      else:
        time.sleep(1)
        botorder = k.query_private('QueryOrders', {'txid' : botcom[0]})['result']
        if botorder[botcom[0]]['status'] == "closed":
          commandesbot[botcom[0]] = botorder[botcom[0]]
        else:
          if float(botorder[botcom[0]]['descr']['price']) <= float(user['LastOrder']):
           retouran = k.query_private('CancelOrder', {'txid' : botcom[0]})['result']
           user['Solde'] = user['Solde'] + user['Mini']
           user['Order'].remove(botcom)
           with open("data.json","w") as outfile:
            json.dump(user, outfile, indent=4)
           with open("data.json","r") as data_file:
            user = json.load(data_file)
      ligne =botorder[botcom[0]]['status'] + ' ' + botorder[botcom[0]]['price']
      profit = float( botorder[botcom[0]]['vol']) * float(cours)
      profit = profit - profit * float(fee) * 0.01
      ligne += " value: " + str(profit)
      profit = profit - float( botorder[botcom[0]]['cost']) - float(botorder[botcom[0]]['fee'])
      ligne += " profit: " + str(profit)
      botord.append(ligne)
    return botord
def Evolution():
        requete = {}
        maxtry = 0
        while 'result' not in requete:
           requete = k.query_public('OHLC',{'pair' : 'XBTEUR', 'interval' : 5})
           maxtry += 1
           if maxtry >= 5:
            break
        histo = requete['result']['XXBTZEUR']
        tendance = []
        lastprice = 0
        for date in histo:
                if float(date[5]) != 0:
                        lastprice = float(date[5])
                        tendance.append(float(date[5]))
                else:
                  if lastprice != 0:
                     tendance.append(lastprice)
        max = len(tendance) - 1
        y = [tendance[max-2],tendance[max-1],tendance[max]]
        x = [0,1,2]
        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
        #trend = [b - a for a, b in zip(tendance[::1], tendance[1::1])]
        #trends = map(str,trend)
        return slope

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
       #self.Affichage = self.add(npyscreen.TitlePager, values=opaff, use_two_lines=True,begin_entry_at=0, max_height=7, name='Operations',editable=False)
       self.Affichageord = self.add(npyscreen.TitlePager, values=ordaff, use_two_lines=True,begin_entry_at=0, max_height=7, name='Operations',editable=False)
       self.botinfo =  self.add(npyscreen.TitleFixedText, value=botinfo, use_two_lines=True,begin_entry_at=0, name='Botinfo',editable=False)
       self.botinfoord = self.add(npyscreen.TitlePager, values=botord, use_two_lines=True,begin_entry_at=0, max_height=11, name='Botorder',editable=False)
       self.keypress_timeout = 30
    def while_waiting(self):
           global iteration
           global itermax
           global commandesbot
           with open("data.json","r") as data_file:
            user = json.load(data_file)
           try:
               reponse = k.query_public('Ticker',{'pair' : 'XBTEUR'})['result']['XXBTZEUR']
               self.botinfoord.values =  refreshbotOrd(user, reponse['c'][0], 0.16)
               self.botinfoord.display()
               trending = Evolution()
               #cours = reponse['c'][0]+ " " + trending[len(trending)-1] + " " + trending[len(trending)-2] + " " + trending[len(trending)-3]
               predi = str(float(reponse['c'][0]) + trending)
               vol = str(user['Mini'] / float(predi))
               cours = reponse['c'][0]+ " " + str(trending) + " " + predi + " " + vol
               self.cours.value = cours
               self.cours.display()
               if iteration >= itermax:
                #self.Affichage.values = refreshOp()
                #self.Affichage.display()
                self.Affichageord.values = refreshOrd()
                #self.Affichageord.values = Evolution()
                self.Affichageord.display()
               else:
                iteration += 1
               if user['Enabled'] == 1:
                   if trending < 0:
                    if user['Solde'] > 0:
                     if float(user['LastOrder']) > float(reponse['c'][0]):
                      neworder = k.query_private('AddOrder',{'pair' : 'XXBTZEUR', 'type' : 'buy', 'ordertype': 'limit', 'price' : predi, 'volume' : vol })['result']
                      user['Solde'] = user['Solde'] - user['Mini']
                      user['LastOrder'] = str(float(predi) - 2.0)
                      self.botinfo.value = "Solde: " + str(user['Solde']) + " Profit: " + str(user['Profit'])
                      self.botinfo.display()
                      user['Order'].append(neworder['txid'])
                      #user['Enabled'] = 0
                      with open("data.json","w") as outfile:
                       json.dump(user, outfile, indent=4)
                      with open("data.json","r") as data_file:
                       user = json.load(data_file)
                   else:
                    if trending > 0:
                     enposit = EnProfit(reponse['c'][0],0.16)
                     for commande in enposit:
                      if commande not in user['EnPosit']:
                       price = reponse['c'][0]
                       vol = enposit[commande]['vol']
                       neworder = k.query_private('AddOrder',{'pair' : 'XXBTZEUR', 'type' : 'sell', 'ordertype': 'limit', 'price' : predi, 'volume' : vol })['result']
                       enposit[commande]['retour'] = neworder['txid']
                       user['EnPosit'][commande] = enposit[commande]
                     with open("data.json","w") as outfile:
                      json.dump(user, outfile, indent=4)
                     with open("data.json","r") as data_file:
                      user = json.load(data_file)
                   for commande in user['EnPosit']:
                      time.sleep(1)
                      etat = k.query_private('QueryOrders', {'txid' : user['EnPosit'][commande]['retour'][0]})['result'][user['EnPosit'][commande]['retour'][0]]
                      if etat['status'] == "closed":
                       user['Profit'] += float(etat['cost']) - float(etat['fee']) - float(user['EnPosit'][commande]['cost']) - float( user['EnPosit'][commande]['fee'])
                       user['Solde'] += 5
                       if float(user['LastOrder']) < float(etat['descr']['price']):
                         user['LastOrder'] = str(float(etat['descr']['price']) - 1.0)
                       user['Order'].remove([commande])
                       del user['EnPosit'][commande]
                       del commandesbot[commande]
                       with open("data.json","w") as outfile:
                        json.dump(user, outfile, indent=4)
                       with open("data.json","r") as data_file:
                        user = json.load(data_file)
                       self.botinfo.value = "Solde: " + str(user['Solde']) + " Profit: " + str(user['Profit'])
                       self.botinfo.display()
                       break

           #except ZeroDivisionError as e:
           except Exception as e:
               pass

class KrakenApp(npyscreen.NPSAppManaged):
   def onStart(self):
       self.addForm('MAIN', Principal, name='Gestion de Kraken')
   def onInMainLoop(self):
       pass

if __name__ == "__main__":
    with open("data.json","r") as data_file:
        user = json.load(data_file)
    k = krakenex.API()
    k.load_key('kraken.key')
    comptes = "test"
    i = 0
    reponse = k.query_public('AssetPairs',{'pair' : 'XBTEUR'})
    demande = k.query_private('Balance')
    if "result" in demande:
      balance = demande['result']
    else:
      print demande['error']
      exit()
    comptes = balance['ZEUR'] + ' euros ' + balance['XXBT'] + ' btc ' + balance['XLTC'] + ' ltc'
    try:
     frais = k.query_private('TradeVolume',{'pair' : 'XBTEUR'})['result']
     fraisachat =  frais['fees_maker']['XXBTZEUR']['fee']
     fraisvente = frais['fees']['XXBTZEUR']['fee']
    except Exception:
     fraisachat =str(0.16)
     fraisvente =str(0.26)
    fees = fraisachat + " " + fraisvente
#    operation = k.query_private('OpenPositions',{'docalcs' : 'true'})['result']
#    opaff = []
    ordaff = []
    botinfo = "Solde: " + str(user['Solde']) + " Profit: " + str(user['Profit'])
#    for op in operation:
#        profit = float(operation[op]['value']) - float(operation[op]['fee']) - float(operation[op]['cost']) - float(operation[op]['value']) * float(fraisachat)*0.01
#        opaff.append(operation[op]['cost'] + ' euros ' + operation[op]['fee'] + ' euros ' + operation[op]['net'] + ' profit ' + str(profit))
    time.sleep(1)
    commandes = k.query_private('OpenOrders',{'trades' : 'true'})['result']['open']
    for commande in commandes:
        ordaff.append(commandes[commande]['descr']['order'])
    reponse = k.query_public('Ticker',{'pair' : 'XBTEUR'})['result']['XXBTZEUR']
    cours = reponse['c'][0]
    botord = refreshbotOrd(user, reponse['c'][0], fraisachat)
    App = KrakenApp().run()
while True:
        reponse = k.query_public('Ticker',{'pair' : 'XBTEUR'})['result']['XXBTZEUR']
        print reponse['c'][0]
        time.sleep(1)

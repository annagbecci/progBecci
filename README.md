## 📚 WEB APPLICATION PER LETTORI 📚

Una web application per appassionati di lettura: esplora libri nei vari generi, scrivi recensioni, gestisci un diario personale, partecipa a eventi con autori e scambia libri con altri utenti.  
Include un sistema di raccomandazione basato su **cosine similarity** per trovare lettori con interessi simili ai tuoi.

Si cerca ispirazione, si lascia traccia delle proprie emozioni, si fa rete.

<img width="1919" height="816" alt="image" src="https://github.com/user-attachments/assets/1a3060bf-1631-4f9f-b4df-97781479f228" />


## Principali funzionalità
- galleria di libri divisi per generi: porta anche alle pagine degli autori o del libro stesso, con relative recensioni di tutti gli utenti
- lista desideri: i libri che un utente vuole tenere presenti per le prossime scelte
- diario personale: per ogni libro letto, un utente può aggiungere delle note (visibili solo dal proprio profilo)
- opportunità di scambio: un utente può selezionare dei libri da rendere disponibili allo scambio, ma anche cercare dei libri da altri utenti
- eventi di presentazione libri con autori in tutta Italia
- recommendation system basato su cosine similarity per suggerire utenti con interessi simili

## Tecnologie utilizzate
- **Backend**: [Django 5.x] – framework principale per la gestione del modello dati, autenticazione utenti e viste.  
- **Database**: [SQLite] (di default in sviluppo)  
- **Librerie Python**:  
  - [NumPy] – supporto per operazioni matematiche nel recommendation system  
  - [Pillow] – gestione delle immagini di profilo degli utenti 
- **Frontend**:  
  - HTML5, CSS3, JavaScript  
  - [Bootstrap 4.6] per layout responsive e componenti UI  
- **Autenticazione**: sistema built-in di Django (esteso con modello `Utente` personalizzato)

##
Realizzato da Becci Anna Grazia,
studentessa del corso di laurea triennale in Ingegneria informatica
##

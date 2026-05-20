# KALK - Interpretator de Pseudocod pentru Clasa a IX-a

## Despre Proiect
**KALK** este un interpretator de limbaj de programare minimalist, creat special pentru elevii de clasa a IX-a care studiază informatica. 

În programa școlară de liceu, o perioadă semnificativă de timp este dedicată învățării algoritmilor prin **pseudocod**, fără a utiliza un limbaj de programare concret (precum C++ sau Pascal). Proiectul KALK vine în sprijinul acestor elevi, oferindu-le un mediu interactiv (IDE) unde pot scrie, testa și executa algoritmi folosiți în clasă, utilizând o sintaxă în limba română, foarte apropiată de cea din manuale.

## Caracteristici Principale
Proiectul a fost dezvoltat pentru a acoperi toate nevoile fundamentale ale algoritmicii de bază:

*   **Sintaxă în Limba Română**: Instrucțiuni intuitive precum `CITESTE`, `SCRIE`, `DACA...ATUNCI`, `CATTIMP...EXECUTA`.
*   **Tipuri de Date**:
    *   Numere întregi și numere cu virgulă mobilă (**floating point**).
    *   **Tablouri unidimensionale (Vectori)**: Suport pentru liste de valori și acces prin index.
*   **Funcții și Recursivitate**: Permite definirea de subprograme cu parametri și returnarea valorilor, facilitând înțelegerea modularizării.
*   **Expresii Complexe**: Suport pentru prioritizarea operațiilor prin paranteze și operatori logici (`SI`, `SAU`).
*   **IDE Integrat**: Interfață grafică dezvoltată în PySide6, cu evidențierea sintaxei (syntax highlighting), auto-indentare și gestionarea bibliotecii de programe.

## Exemplu de Cod
```
FUNCTIE factorial(n)
    DACA n <= 1 ATUNCI
        RETURNEAZA 1
    SFARSIT
    RETURNEAZA n * factorial(n - 1)
SFARSIT

CITESTE numar
DECLAR f VALOARE factorial(numar)
SCRIE f
```

## Instalare și Rulare
Pentru a rula proiectul, aveți nevoie de Python 3 și biblioteca PySide6 instalată.

1. Clonează depozitul:
   ```bash
   git clone https://github.com/fl9ppy/kalk.git
   ```
2. Instalează dependențele:
   ```bash
   pip install PySide6
   ```
3. Rulează aplicația:
   ```bash
   python main.py
   ```

## Tehnologii Utilizate
*   **Python**: Limbajul de bază pentru motorul de execuție.
*   **Lexer & Parser**: Implementare proprie pentru analiza lexicală și sintactică a codului.
*   **PySide6 (Qt)**: Pentru interfața grafică a utilizatorului.

## Licență
Acest proiect este licențiat sub **Licența MIT**. 
Licențiat către: **fl9ppy** (GitHub).

---
*Creat ca proiect final pentru atestatul de informatică.*

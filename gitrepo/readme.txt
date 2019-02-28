0) Ensure symbols.txt have all the symbols for which the data needs to be fetched

1) Running getData.py - Ensure the rootFolder path is changed to the folder location of data which have the transcript files downloaded
python getData.py

2) Running pushToES.py - Change the end point of API to the right string
python pushToES.py

3) Open index.html to view the data by entering the symbol in the search bar 
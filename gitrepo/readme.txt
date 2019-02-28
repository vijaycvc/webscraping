0) Ensure dataprocessing/symbols.txt have all the symbols for which the data needs to be fetched

1) Running dataprocessing/getData.py - Ensure the rootFolder path is changed to the folder location of data which have the transcript files downloaded
python getData.py

2) Running dataprocessing/pushToES.py - Change the end point of API to the right string
python pushToES.py

3) Open web/index.html to view the data by entering the symbol in the search bar 

4) data folder has the data which is temporarily downloaded

5) dataprocessing/YYYY/MM/DD/HH is the folder structure for the data extracted which will be pushed to ES

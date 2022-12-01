ep=$1

convert train_A/${ep}.png train_B/${ep}.png +append tmp.png

display tmp.png 

rm tmp.png


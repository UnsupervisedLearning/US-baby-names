# US-baby-names

Data from https://www.kaggle.com/kaggle/us-baby-names


## Example usage

Compare multiple names:

	python name_frequency.py --names Wells Howard Jamie Louis Darren --gender=M -o namePlot_compare.png

Normalize and compare shapes of names:

	python name_frequency.py --names Darren Daren Darin --gender=M -o namePlot_Darrens_norm.png --normalize

Plot single name and year when individual with that name was born:

	python name_frequency.py --names=Darren --year=1982 --gender=M

Get help menu with option arguments:

	python name_frequency.py --help

#!/usr/bin/python3

'''
# VexDesign
A script that autonomously designs a vaccine. Authored by Sari Sabban on 31-May-2017 (sari.sabban@gmail.com).

## Requirements:
1. Make sure you install [PyRosetta](http://www.pyrosetta.org) as the website describes.
2. Use the following commands (in GNU/Linux) to install all nessesary Python libraries for this script to run successfully:

`sudo apt install python3-pip pymol DSSP gnuplot`

`sudo python3 -m pip install zeep numpy biopython bs4`

## How To Use:
1. Use the following command to run the script:

`python3 VaxDesign.py PDBID CHAIN FROM TO`

* PDBID = The protein's [Protein Data Bank](https://www.rcsb.org) identification name.
* CHAIN = The chain where your target site resides within the protein .pdb file.
* FROM = the start of your target site.
* TO = the end of your target site.

2. Calculation time is about 72 hours.
3. Access to the internet is a requirement since the script will be sending and retrieving data from several servers.

## Description
This script autonomously designs a vaccine from a user specified target site. This is not artificial intellegance, you cannot just ask the the script to design "A" vaccine, you must understand what target site you want to develop antibodies against (make a liturature search and understand your disease and target site), then supply this target site to the script to build a protein structure around it so the final protein can be used as a vaccine. You must have prior understanding of Bioinformatics and Immunology in order to be able to understand what site to target and to supply it to the script. Once you identify a target site, the script will take it and run a long protocol, without the need for you to intervene, that will result in an ideal protein structure displaying your target site in its original 3D cofiguration. Thus the protien, theoretically, can be used as a vaccine against this site, and hopefully neutralise the disease you are researching. Everytime you run this script a different final protien structure will be generated, this is important to keep in mind, because if you want to generate many different structures to test or to use as boosts you can simply run the same target site again and you will end up with a different final structure.

Here is a [video](youtube.com/) that explains how to select a target site, how the script functions, and what results you get. If I did not make a video yet, bug me until I make one.

The script protocol is as follows:
* STILL UNDERT DEVELOPMENT

python3 VaxDesign.py 2y7q B 36 37
'''

#Import Modules
                               #Modules to download---> #      #       #	#
import sys , os , re , time , datetime , subprocess , zeep , numpy , Bio.PDB , bs4 , random , requests , urllib.request

#Terminal Text Colours
Black 	= '\x1b[30m'
Red	= '\x1b[31m'
Green	= '\x1b[32m'
Yellow	= '\x1b[33m'
Blue	= '\x1b[34m'
Purple	= '\x1b[35m'
Cyan	= '\x1b[36m'
White	= '\x1b[37m'
Cancel	= '\x1b[0m'

#Welcome Text
print(Green + '''
  ██╗   ██╗ █████╗ ██╗  ██╗
  ██║   ██║██╔══██╗╚██╗██╔╝
  ██║   ██║███████║ ╚███╔╝ 
  ╚██╗ ██╔╝██╔══██║ ██╔██╗ 
   ╚████╔╝ ██║  ██║██╔╝ ██╗
    ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═╝
                           
  ██████╗ ███████╗███████╗██╗ ██████╗ ███╗   ██╗
  ██╔══██╗██╔════╝██╔════╝██║██╔════╝ ████╗  ██║
  ██║  ██║█████╗  ███████╗██║██║  ███╗██╔██╗ ██║
  ██║  ██║██╔══╝  ╚════██║██║██║   ██║██║╚██╗██║
  ██████╔╝███████╗███████║██║╚██████╔╝██║ ╚████║
  ╚═════╝ ╚══════╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
                                                
''' + Cancel)
print(Purple + '''
  ╔═╗┬ ┬┌┬┐┌─┐  ╔╦╗┌─┐┌─┐┬┌─┐┌┐┌  ╔═╗  ╦  ╦┌─┐┌─┐┌─┐┬┌┐┌┌─┐
  ╠═╣│ │ │ │ │   ║║├┤ └─┐││ ┬│││  ╠═╣  ╚╗╔╝├─┤│  │  ││││├┤ 
  ╩ ╩└─┘ ┴ └─┘  ═╩╝└─┘└─┘┴└─┘┘└┘  ╩ ╩   ╚╝ ┴ ┴└─┘└─┘┴┘└┘└─┘
''' + Cancel)
print(Yellow+ 'Authored by Sari Sabban on 31-May-2017 (sari.sabban@gmail.com)' + Cancel)
print(Cyan + '--------------------------------------------------------------' + Cancel)
time.sleep(3)

#Import PyRosetta, its Tools, and its Database
from pyrosetta import *
from pyrosetta.toolbox import *
from pyrosetta.rosetta.protocols.relax import *
from pyrosetta.rosetta.protocols.moves import *
from pyrosetta.rosetta.protocols.simple_moves import *
from pyrosetta.rosetta.protocols.denovo_design.movers import *
from pyrosetta.rosetta.protocols.toolbox.pose_metric_calculators import *
from pyrosetta.rosetta.core.fragment import *
from pyrosetta.rosetta.core.pack.task import *
from pyrosetta.rosetta.core.scoring.packstat import *
from pyrosetta.rosetta.core.pack.task.operation import *
from pyrosetta.rosetta.core.pack.task import TaskFactory
init()

#User Inputs
Protein		= sys.argv[1]
Chain		= sys.argv[2]
Motif_from	= sys.argv[3]
Motif_to	= sys.argv[4]
#--------------------------------------------------------------------------------------------------------------------------------------
#The Functions

#1 - Find Path To PyRosetta
def Find(Filename):
	''' Find path to PyRosetta '''
	''' Returns string with path '''
	result = []
	for root , dirs , files in os.walk('/'):
		if Filename in files:
			result.append(os.path.join(root))
	return(result[0]+'/')

#2 - Extract Motif
def Motif(PDB_ID , Chain , Motif_From , Motif_To):
	''' This function downloads a spesific protein from RCSB and isolates a specific user defined motif from it '''
	''' Generates the motif.pdb file '''
	#Get the protein
	os.system('wget http://www.rcsb.org/pdb/files/' + PDB_ID + '.pdb')
	pdb = open(PDB_ID + '.pdb' , 'r')
	#Isolate the motif
	Motif = open('motif.pdb' , 'w')
	count = 0
	num = 0
	AA2 = None
	for line in pdb:
		if not line.startswith('ATOM'):				#Ignore all lines that do not start with ATOM
			continue
		if not line.split()[4] == Chain:			#Ignore all lines that do not have the specified chain (column 5)
			continue
		if str(Motif_From) <= line.split()[5] <= str(Motif_To):	#Find residues between the user specified location
			count += 1					#Sequencially number atoms
			AA1 = line[23:27]				#Sequencially number residues
			if not AA1 == AA2:
				num += 1			
			final_line = line[:7] + '{:4d}'.format(count) + line[11:17] + line[17:21] + 'A' + '{:4d}'.format(num) + line[26:]	#Update each line of the motif to have its atoms and residues sequencially labeled, as well as being in chain A
			AA2 = AA1
			Motif.write(final_line)				#Write to new file called motif.pdb
	Motif.close()
	#Keep working directory clean
	os.remove(PDB_ID + '.pdb')					#Remove the protein's original file

#3 - PyMOL Visualisation
class PyMol():
	#3.1 - Setup PyMOL For Visualisation
	def Start():
		''' Starts PyMOL and allows it to listen to PyRosetta ''' 
		''' Opens PyMOL '''
		PATH = Find('PyMOL-RosettaServer.py')										#Find path to PyRosetta
		Temp = open('temp.py' , 'w')											#Open a python temporary file so from it PyMol setup commands can be run
		Temp.write("import pymol\npymol.finish_launching()\ncmd.show_as('cartoon')\ncmd.set('cavity_cull', 0)\n")	#Write to temporary file the PyMol setup commands
		Temp.write("cmd.do('run " + PATH + "PyMOL-RosettaServer.py')")							#Commands from within PyMol to make PyMol listen to PyRosetta
		Temp.close()
		new_terminal = "x-terminal-emulator -e pymol temp.py".split()							#Command to open a new terminal window and run from it PyMol opening the temporary file
		processes = [subprocess.Popen(new_terminal)]									#Execute new terminal window command
		time.sleep(5)													#Sleep for 5 seconds to allow PyMol to load up fully and start listening before anything else happens
		AddPyMOLObserver(test, True)											#Every time a change is happens in the pose coordinates PyMOL will keep a history of the changed and save it in different frames
		os.remove('temp.py')												#Keep working directory clea
	#3.2 - Live PyMOL Visualisation:
	def Update(pose):
		''' Transmits what is happening to a structure in PyRosetta to PyMol '''
		''' Shows structure in PyMol or updates PyMol with new structure '''
		pymol = PyMOLMover()		#Load the PyMOLMover
		pymol.apply(pose)		#Transmit the pose to PyMol
		pymol.send_ss(pose , ss = '')	#Show secondary structures as cartoon
		pymol.keep_history(True)	#To keep separate frames for each conformation as we modify it
		#colouring
		#pymol.send_colors(pose , rosetta.std.map_int_int() , default_color=rosetta.protocols.moves.XC_green)		#Only Change XC_green to XC_red or any other colour
	#3.3 - Show Each Residue's Energy
	def Energy(pose):
		''' Transmits what is happening to a structure in PyRosetta to PyMol '''
		''' Shows each residue's energy (red = high) (blue = low) '''
		pymol = PyMOLMover()
		scorefxn = get_fa_scorefxn()
		scorefxn(pose)
		pymol.apply(pose)
		pymol.send_energy(pose)

#4 - Get Score of Structure
class Score():
	#4.1 - Get Score For The Whole Structure
	def ALL(pose):
		''' Scores a protein's structure '''
		''' Returns an integer as the protein's score '''
		scorefxn = get_fa_scorefxn()	#Load the score function
		return(scorefxn(pose))		#Score the portein and print its value
	#4.2 - Get Score For Each Single Residue
	def AA(pose):
		''' Scores each single amino acid within a protein's structure seperatly'''
		''' Returns a tuple with list of Residue numbers [0], Residue Types [1], Scores [2] '''
		scorefxn = get_fa_scorefxn()						#Load the score function
		scorefxn(pose)								#Score the portein and update the pose
		size = pose.total_residue()						#Get the size (number of residues) of the protein
		count = 0
		Number = list()
		Residue = list()
		Score = list()
		for AA in range(size):							#Loop through each residue
			count += 1							#Position of the residue
			residue = pose.residue(count).name()				#Get name of residue
			Res_Score = pose.energies().residue_total_energy(count)		#Get total energy of the residue
			if Res_Score >= 0:						#If residue has a score more than 0 show it
				Number.append(count)
				Residue.append(residue)
				Score.append(Res_Score)
		#List of residue numbers [0], Residue Types [1], Scores [2]
		return(Number , Residue , Score)

#5 - PSIPRED
def PSIPRED(pose):
	''' Submits an amino acid sequence to the PsiPred server at UCL for accurate secondary structure prediction, returns a string alignment with the prediction '''
	''' Generates the PSIPRED.psipred file '''
	#The PsiPred server at UCL uses SOAP to allow us to interact with it (the zeep module allows the of SOAP in python)
	client = zeep.Client('http://bioinf.cs.ucl.ac.uk/psipred_api/wsdl')						#Load the PSIPRED WSDL into a variable
	email = 'acresearch@icloud.com'											#Email is required for submission
	title = 'scaffold'												#A submission title is required for submission
	#Submit
	sequence = pose.sequence()
	Submission = client.service.PsipredSubmit(sequence , email , title , 'True' , 'False' , 'False' , 'all')	#Method from WSDL to submit a protein's sequence for PSIPRED, zeep returns a dictionary so save to a variable
	job_id = Submission['job_id']											#Get the job ID from the dictionary for next step
	print(Green + '[+] Sequence submitted to PSIPRED server at University College London' + Cancel)
	#Get Result
	#Not an infinite loop, this is to break the script (after 6:00 hours) if there are problems with the PSIPRED server (it sometimes happens)
	for attempt in ['0:15' , '0:30' , '0:45' , '1:00' , '1:15' , '1:30' , '1:45' , '2:00' , '2:15' , '2:30' , '2:45' , '3:00' , '3:15' , '3:30' , '3:45' , '4:00' , '4:15' , '4:30' , '4:45' , '5:00' , '5:15' , '5:30' , '5:45' , '6:00']:
		Result = client.service.PsipredResult(job_id)								#Quiry for results, zeep returns a dictionary so save to a variable
		URL = Result['psipred_results']										#Get the result's download file's URL
		try:
			if URL == None:											#if no URL available (because server is still running) check again in 15 minutes
				print(Red + '[-] PSIPRED server calculation not yet complete - check again in 15 minutes' + Cancel)
				time.sleep(900)
				continue
			else:
				os.system('wget ' + URL)								#When result's download file's URL is available download the file
				print(Green + '[+] PSIPRED server calculation complete' + Cancel)
				break
		except Exception as TheError:
			print(Red + '[-] ERROR: No response from server' + Cancel)
	#Rename
	time.sleep(3)
	URL = URL.split('/')
	os.rename(URL[5] , 'temp.psipred')
	#Modify to be aligned
	temp = open('temp.psipred' , 'r')	#Open the PSIPRED's downloaded file
	PSI = open('PSIPRED.psipred' , 'w')	#Generate the final PSIPRED.psipred file
	Conf = list()
	Pred = list()
	AA = list()
	for line in temp:
		if line.startswith('Conf'):
			line = line.split()
			Conf.append(line[1])
		elif line.startswith('Pred'):
			line = line.split()
			Pred.append(line[1])
		elif line.startswith('  AA'):
			line = line.split()
			AA.append(line[1])
	conf = ''.join(Conf)
	pred = ''.join(Pred)
	aa = ''.join(AA)
	PSI.write('Conf: ' + conf + '\n')
	PSI.write('Pred: ' + pred + '\n')
	PSI.write('  AA: ' + aa + '\n')
	time.sleep(3)
	os.remove('temp.psipred')		#Keep working directory clean, remove the temp.psipred file
	print(Green + '[+] PSIPRED prediction complete' + Cancel)

#6 - Get Surface, Boundery, and Core
def ProtLayers(Filename):
	''' Takes A .pdb protein structure file, finds each layer of the protein (Surface, Boundery, Core) and returns the residue number of each amino acid and which layer it corresponds to '''
	''' Returns a tuple with residue number for Surface [0], Boundery [1], Core [2] '''
	#Standard script to setup biopython's DSSP to calculate SASA using Wilke constants (Tien et.al., 2013 - PMID: 24278298)
	p = Bio.PDB.PDBParser()
	structure = p.get_structure('X' , Filename)
	model = structure[0]
	dssp = Bio.PDB.DSSP(model , Filename , acc_array='Wilke')
	#Loop to isolate SASA for each amino acid
	lis = list()
	for x in dssp:
		if x[1]=='A' : sasa=129*(x[3])
		elif x[1]=='V' : sasa=174*(x[3])
		elif x[1]=='I' : sasa=197*(x[3])
		elif x[1]=='L' : sasa=201*(x[3])
		elif x[1]=='M' : sasa=224*(x[3])
		elif x[1]=='P' : sasa=159*(x[3])
		elif x[1]=='Y' : sasa=263*(x[3])
		elif x[1]=='F' : sasa=240*(x[3])
		elif x[1]=='W' : sasa=285*(x[3])
		elif x[1]=='R' : sasa=274*(x[3])
		elif x[1]=='N' : sasa=195*(x[3])
		elif x[1]=='C' : sasa=167*(x[3])
		elif x[1]=='Q' : sasa=225*(x[3])
		elif x[1]=='E' : sasa=223*(x[3])
		elif x[1]=='G' : sasa=104*(x[3])
		elif x[1]=='H' : sasa=224*(x[3])
		elif x[1]=='K' : sasa=236*(x[3])
		elif x[1]=='S' : sasa=155*(x[3])
		elif x[1]=='T' : sasa=172*(x[3])
		elif x[1]=='D' : sasa=193*(x[3])
		lis.append((x[2] , sasa))
	#Label each amino acid but record its residue number
	core = list()
	boundery = list()
	surface = list()
	count = 0
	for x , y in lis:
		count = count + 1
		#Loop
		if y <= 25 and (x == '-' or x == 'T' or x == 'S'):		#Label each amino acid depending on its SASA position according to the parameters highlighted in the paper by (Koga et.al., 2012 - PMID: 23135467). The parameters are as follows:
			core.append(count)					#Surface:
		elif 25 < y < 40 and (x == '-' or x == 'T' or x == 'S'):	#	Helix or Sheet:	SASA >= 60
			boundery.append(count)					#	Loop:		SASA >= 40
		elif y >= 40 and (x == '-' or x == 'T' or x == 'S'):		#
			surface.append(count)					#Boundry:
		#Helix								#	Helix or Sheet:	15 < SASA < 60
		elif y <= 15 and (x == 'G' or x == 'H' or x == 'I'):		#	Loop:		25 < SASA < 40
			core.append(count)					#
		elif 15 < y < 60 and (x == 'G' or x == 'H' or x == 'I'):	#Core:
			boundery.append(count)					#	Helix or Sheet:	SASA <= 15
		elif y >= 60 and (x == 'G' or x == 'H' or x == 'I'):		#	Loop:		SASA <= 25
			surface.append(count)					#
		#Sheet								#DSSP labels:
		elif y <= 15 and (x == 'B' or x == 'E'):			#Loop =		- or T or S
			core.append(count)					#Helix =	G or H or I
		elif 15 < y < 60 and (x == 'B' or x == 'E'):			#Sheet =	B or E
			boundery.append(count)
		elif y >= 60 and (x == 'B' or x == 'E'):
			surface.append(count)
	#Return result: Surface is [0], Boundery is [1], Core is [2]
	return(surface , boundery , core)

#7 - Probability To Make A Choice
def Decision(score_before , score_after):
	''' Metropolis Criterion, P = 1 to accept all structures when final score is lower than starting score, P closer to 0 = accept less and less but sometimes accept to escape local energy minima '''
	''' Returns a string with either Accept or Reject '''
	E = score_after - score_before		#Takes the difference between the score before and after a change in a structure
	if E >= 0:				#If the score after change is larger than the score before change have low P value
		negE = E * -1
		kt = 1
		e = math.e
		P = e**(negE/kt)
	elif E < 0:				#If the score after change is larger than the score before change have P of 1
		P = 1
	if (random.random() < P) == True:	#Randomly accept or reject the score difference. Probability to accept increases as P gets closer to 1
		return('Accept')
	else:
		return('Reject')

#8 - RosettaRelax
def Relax(pose):
	''' Relaxes a structure '''
	''' Updates the original pose with the relaxed pose '''
	scorefxn = get_fa_scorefxn()
	relax = FastRelax()
	relax.set_scorefxn(scorefxn)
	relax.apply(pose)

#9 - SASA
def SASA(pose):
	''' Calculates the different layers (Surface, Boundery, Core) of a structure according its SASA (solvent-accessible surface area) '''
	''' Returns three lists Surface amino acids = [0] , Boundery amino acids = [1] , Core amino acids = [2] '''
	#Temporary generate a .pdb file of the pose to isolate the layers since it is not yet possible to do that using a Rosetta pose, this temporary .pdb file will be deleted after the layers are found
	pose.dump_pdb('ToDesign.pdb')
	#Standard script to setup biopython's DSSP to calculate SASA using Wilke constants
	p = Bio.PDB.PDBParser()
	structure = p.get_structure('X' , 'ToDesign.pdb')
	model = structure[0]
	dssp = Bio.PDB.DSSP(model , 'ToDesign.pdb' , acc_array='Wilke')
	#Loop to get SASA for each amino acid
	lis = list()
	count = 0
	for x in dssp:
		if x[1]=='A' : sasa=129*(x[3])
		elif x[1]=='V' : sasa=174*(x[3])
		elif x[1]=='I' : sasa=197*(x[3])
		elif x[1]=='L' : sasa=201*(x[3])
		elif x[1]=='M' : sasa=224*(x[3])
		elif x[1]=='P' : sasa=159*(x[3])
		elif x[1]=='Y' : sasa=263*(x[3])
		elif x[1]=='F' : sasa=240*(x[3])
		elif x[1]=='W' : sasa=285*(x[3])
		elif x[1]=='R' : sasa=274*(x[3])
		elif x[1]=='C' : sasa=167*(x[3])
		elif x[1]=='N' : sasa=195*(x[3])
		elif x[1]=='Q' : sasa=225*(x[3])
		elif x[1]=='E' : sasa=223*(x[3])
		elif x[1]=='G' : sasa=104*(x[3])
		elif x[1]=='H' : sasa=224*(x[3])
		elif x[1]=='K' : sasa=236*(x[3])
		elif x[1]=='S' : sasa=155*(x[3])
		elif x[1]=='T' : sasa=172*(x[3])
		elif x[1]=='D' : sasa=193*(x[3])
		lis.append((x[2] , sasa))
	#Label each amino acid depending on its SASA position according to the parameters highlighted in the paper by (Koga et.al., 2012 - PMID: 23135467). The parameters are as follows:
	#Surface:	Helix or Sheet: SASA => 60		Loop: SASA => 40
	#Boundry:	Helix or Sheet: 15 < SASA < 60		Loop: 25 < SASA < 40
	#Core:		Helix or Sheet: SASA =< 15		Loop: SASA =< 25	
	surface = list()
	boundery = list()
	core = list()
	count = 0
	for x , y in lis:
		count = count + 1
		if y <= 25 and (x == '-' or x == 'T' or x == 'S'):		#Loop (DSSP code is - or T or S)
			core.append(count)
		elif 25 < y < 40 and (x == '-' or x == 'T' or x == 'S'):	#Loop (DSSP code is - or T or S)
			boundery.append(count)
		elif y >= 40 and (x == '-' or x == 'T' or x == 'S'):		#Loop (DSSP code is - or T or S)
			surface.append(count)
		elif y <= 15 and (x == 'G' or x == 'H' or x == 'I'):		#Helix (DSSP code is G or H or I)
			core.append(count)
		elif 15 < y < 60 and (x == 'G' or x == 'H' or x == 'I'):	#Helix (DSSP code is G or H or I)
			boundery.append(count)
		elif y >= 60 and (x == 'G' or x == 'H' or x == 'I'):		#Helix (DSSP code is G or H or I)
			surface.append(count)
		elif y <= 15 and (x == 'B' or x == 'E'):			#Sheet (DSSP code is B or E)
			core.append(count)
		elif 15 < y < 60 and (x == 'B' or x == 'E'):			#Sheet (DSSP code is B or E)
			boundery.append(count)
		elif y >= 60 and (x == 'B' or x == 'E'):			#Sheet (DSSP code is B or E)
			surface.append(count)	
	os.remove('ToDesign.pdb')						#Keep working directory clean
	return(surface , boundery , core)

#10 - RosettaDesign
class Design():
	#10.1 - Design Whole Structure All At Once
	def Whole(pose):
		''' Applies RosettaDesign to change the whole structure's amino acids (the whole structure all at once) while maintaining the same backbone '''
		''' Just updates the pose with the new structure '''
		#1 - Relax original structure
		scorefxn = get_fa_scorefxn()							#Call the score function
		score1_original_before_relax = scorefxn(pose)					#Measure score before relaxing
		Relax(pose)									#Relax structure
		score2_original_after_relax = scorefxn(pose)					#Measure score after relaxing
		#2 - Preform RosettaDesign for whole structure
		for inter in range(3):
			task_pack = standard_packer_task(pose)
			pack_mover = PackRotamersMover(scorefxn , task_pack)
			pack_mover.apply(pose)
			#3 - Relax pose
			Relax(pose)
		score3_of_design_after_relax = scorefxn(pose)					#Measure score of designed pose
		#pose.dump_pdb('Designed.pdb')							#Export final pose into a .pdb structure file
		print(score1_original_before_relax)
		print(score2_original_after_relax)
		print(score3_of_design_after_relax)
	#10.2 - Design The Structure Once Layer At A Time
	def Layer(pose):
		''' Applies RosettaDesign to change the whole structure's amino acids (one layer at a time) while maintaining the same backbone. It is efficient and faster than the previous method (Design_Full) '''
		''' Just updates the pose with the new structure '''
		#Relax original structure
		scorefxn = get_fa_scorefxn()							#Call the score function
		score1_original_before_relax = scorefxn(pose)					#Measure score before relaxing
		Relax(pose)									#Relax structure
		score2_original_after_relax = scorefxn(pose)					#Measure score after relaxing
		#Preform RosettaDesign one layer at a time
		for inter in range(3):
			#1 - Get SASA Layers
			sasa = SASA(pose)
			surface = sasa[0]
			boundry = sasa[1]
			core = sasa[2]
			#2 - Preform RosettaDesign on each layer
			#Design core
			task_pack = standard_packer_task(pose)
			pack_mover = PackRotamersMover(scorefxn , task_pack)
			task_pack.temporarily_fix_everything()					#To prevent all amino acids from being designed
			for AA in core:
				coreAA = pose.residue(AA).name()
				if coreAA == 'CYS:disulfide':
					continue
				else:
					task_pack.temporarily_set_pack_residue(AA , True)	#To move only spesific amino acids
			pack_mover.apply(pose)
			#Design boundery
			task_pack = standard_packer_task(pose)
			pack_mover = PackRotamersMover(scorefxn , task_pack)
			task_pack.temporarily_fix_everything()					#To prevent all amino acids from being designed
			for AA in boundry:
				boundAA = pose.residue(AA).name()
				if boundAA == 'CYS:disulfide':
					continue
				else:
					task_pack.temporarily_set_pack_residue(AA , True)	#To move only spesific amino acids
			pack_mover.apply(pose)
			#Design surface
			task_pack = standard_packer_task(pose)
			pack_mover = PackRotamersMover(scorefxn , task_pack)
			task_pack.temporarily_fix_everything()					#To prevent all amino acids from being designed
			for AA in surface:
				surfAA = pose.residue(AA).name()
				if surfAA == 'CYS:disulfide':
					continue
				else:
					task_pack.temporarily_set_pack_residue(AA , True)	#To move only spesific amino acids
			pack_mover.apply(pose)
			#3 - Relax pose
			Relax(pose)
		score3_of_design_after_relax = scorefxn(pose)					#Measure score of designed pose
		#pose.dump_pdb('Designed.pdb')							#Export final pose into a .pdb structure file
		print(score1_original_before_relax)
		print(score2_original_after_relax)
		print(score3_of_design_after_relax)
	#10.3 - Design The Structure One Layer At A Time Moving Towards A Tightly Packed Core With Every Loop
	def Pack(pose):
		''' Applies FastDesign to change the whole structure's amino acids (one layer at a time as well as designing towards an optimally packed core) while maintaining the same backbone. Should be faster than the Whole method and results in a better final structure than the Layer method '''
		''' Generates the Designed.pdb file '''
		#A - Relax original structure
		scorefxn = get_fa_scorefxn()							#Call the score function
		score1_original_before_relax = scorefxn(pose)					#Measure score before relaxing
		Relax(pose)									#Relax structure
		score2_original_after_relax = scorefxn(pose)					#Measure score after relaxing
		#B - FastDesign Protocol							#Uses Generic Monte Carlo with PackStat as a filter to direct FastDesign towards an optimally packed structure core
		layers = [2 , 1 , 0]								#Layer Identity from SASA Surface = [0] , Boundary = [1] , Core = [2]
		for identity in layers:								#Loop through each layer
			#1 - Setup The PackStat Filter
			filters = rosetta.protocols.simple_filters.PackStatFilter()
			#2 - Identify The Layers
			sasa = SASA(pose)							#Re-calculate SASA every time because amino acid position can change from one layer to another during the design phase, therefore make sure to design the layer not the amino acid
			layer = sasa[identity]							#Changes every iteration to start with Core (sasa[2]) then Boundary (sasa[1]) then Surface (sasa[0])
			#3 - Generate The Resfile						#Will generate a new Resfile for each layer (which is why it is deleted at the end of the loop)
			Resfile = open('Resfile.resfile' , 'w')
			Resfile.write('NATAA\n')
			Resfile.write('start\n')
			for line in layer:
				Resfile.write(str(line) + ' A ALLAA\n')
			Resfile.close()
			#4 - Setup The FastDesign Mover
			task = TaskFactory()							#Setup the TaskFactory
			read = ReadResfile('Resfile.resfile')					#Call the generated Resfile
			task.push_back(read)							#Add the Resfile to the TaskFactory
			movemap = MoveMap()							#Setup the MoveMap
			movemap.set_bb(False)							#Do not change the phi and psi BackBone angles
			movemap.set_chi(True)							#Change the chi Side Chain angle
			mover = FastDesign()							#Call the FastDesign Mover
			mover.set_task_factory(task)						#Add the TaskFactory to it
			mover.set_movemap(movemap)						#Add the MoveMap to it
			mover.set_scorefxn(scorefxn)						#Add the Score Function to it
			#5 - Setup and Apply The Generic Monte Carlo Mover
			MC = GenericMonteCarloMover()						#Call Monter Carlo Class
			MC.set_mover(mover)							#Load The Mover
			MC.set_scorefxn(scorefxn)						#Set score function
			MC.set_maxtrials(10)							#Set number of monte carlo loops
			MC.set_temperature(1)							#Set temperature
			MC.set_preapply(True)							#To apply Boltzmann accept/reject to all applications of the mover (always use False)
			MC.set_drift(True)							#Make current pose = next iteration pose
			MC.set_sampletype('high')						#Move monte carlo to higher filter score
			MC.recover_low(True)							#True - at the end of application, the pose is set to the lowest (or highest if sample_type="high") scoring pose
			#MC.stopping_condition()						#Stops before trials are done if a filter evaluates to true
			MC.add_filter(filters , False , 1.0 , 'high' , True)			#Add a filter (Filter Type , Adaptive , Temperature , Sample Type , Rank By)
			#MC.task_factory(task) #Causes an infinite loop				#Include a Task Factory
			#MC.boltzmann(pose) #For some reason hates a relaxed pose		#Evaulates a pose based on the scores/filters + temperatures
			MC.apply(pose)								#Apply Move
			os.remove('Resfile.resfile')						#To keep working directory clean, and to make sure each Resfile has the info for each layer only and they do not get mixed and appended together in one Resfile
		#C - Relax Pose
		Relax(pose)									#Relax structure
		#D - Output Result
		score3_of_design_after_relax = scorefxn(pose)					#Measure score of designed pose
		pose.dump_pdb('Designed.pdb')							#Export final pose into a .pdb structure file
		print('---------------------------------------------------------')
		print('Original Structure Score:' , '\t' , score1_original_before_relax)
		print('Relaxed Original Score:' , '\t' , score2_original_after_relax)
		print('Relaxed Design Score:' , '\t\t' , score3_of_design_after_relax)
	#10.4 - Design The Structure One Layer At A Time, Except For A Desired Motif, Moving Towards A Tightly Packed Core With Every Loop
	def Motif(pose , Motif_From , Motif_To):
		''' Applies RosettaDesign to change the structure's amino acids (one layer at a time - like in the Design_Layer method) except for a desired continuous motif sequence while maintaining the same backbone '''
		''' Just updates the pose with the new structure '''
		#A - Relax original structure
		Motif = list(range(int(Motif_From) , int(Motif_To) + 1))			#Identify motif residues
		scorefxn = get_fa_scorefxn()							#Call the score function
		score1_original_before_relax = scorefxn(pose)					#Measure score before relaxing
		Relax(pose)									#Relax structure
		score2_original_after_relax = scorefxn(pose)					#Measure score after relaxing
		#B - FastDesign protocol							#Uses Generic Monte Carlo with PackStat as a filter to direct FastDesign towards an optimally packed structure core
		layers = [2 , 1 , 0]								#Layer Identity from SASA Surface = [0] , Boundary = [1] , Core = [2]
		for identity in layers:								#Loop through each layer
			#1 - Setup the PackStat filter
			filters = rosetta.protocols.simple_filters.PackStatFilter()
			#2 - Identify the layers
			sasa = SASA(pose)							#Re-calculate SASA every time because amino acid position can change from one layer to another during the design phase, therefore make sure to design the layer not the amino acid
			layer = sasa[identity]							#Changes every iteration to start with Core (sasa[2]) then Boundary (sasa[1]) then Surface (sasa[0])
			#3 - Remove motif residues as to not get designed
			layer = list(set(layer) - set(Motif))
			#4 - Generate the resfile						#Will generate a new Resfile for each layer (which is why it is deleted at the end of the loop)
			Resfile = open('Resfile.resfile' , 'w')
			Resfile.write('NATAA\n')
			Resfile.write('start\n')
			for line in layer:
				Resfile.write(str(line) + ' A ALLAA\n')
			Resfile.close()
			#5 - Setup the FastDesign mover
			task = TaskFactory()							#Setup the TaskFactory
			read = ReadResfile('Resfile.resfile')					#Call the generated Resfile
			task.push_back(read)							#Add the Resfile to the TaskFactory
			movemap = MoveMap()							#Setup the MoveMap
			movemap.set_bb(False)							#Do not change the phi and psi BackBone angles
			movemap.set_chi(True)							#Change the chi Side Chain angle
			mover = FastDesign()							#Call the FastDesign Mover
			mover.set_task_factory(task)						#Add the TaskFactory to it
			mover.set_movemap(movemap)						#Add the MoveMap to it
			mover.set_scorefxn(scorefxn)						#Add the Score Function to it
			#6 - Setup and apply the Generic Monte Carlo mover
			MC = GenericMonteCarloMover()						#Call Monter Carlo Class
			MC.set_mover(mover)							#Load The Mover
			MC.set_scorefxn(scorefxn)						#Set score function
			MC.set_maxtrials(10)							#Set number of monte carlo loops
			MC.set_temperature(1)							#Set temperature
			MC.set_preapply(True)							#To apply Boltzmann accept/reject to all applications of the mover (always use False)
			MC.set_drift(True)							#Make current pose = next iteration pose
			MC.set_sampletype('high')						#Move monte carlo to higher filter score
			MC.recover_low(True)							#True - at the end of application, the pose is set to the lowest (or highest if sample_type="high") scoring pose
			#MC.stopping_condition()						#Stops before trials are done if a filter evaluates to true
			MC.add_filter(filters , False , 1.0 , 'high' , True)			#Add a filter (Filter Type , Adaptive , Temperature , Sample Type , Rank By)
			#MC.task_factory(task) #Causes an infinite loop				#Include a Task Factory
			#MC.boltzmann(pose) #For some reason hates a relaxed pose		#Evaulates a pose based on the scores/filters + temperatures
			MC.apply(pose)								#Apply Move
			os.remove('Resfile.resfile')						#To keep working directory clean, and to make sure each Resfile has the info for each layer only and they do not get mixed and appended together in one Resfile
		#C - Relax pose
		Relax(pose)									#Relax structure
		#D - Output result
		score3_of_design_after_relax = scorefxn(pose)					#Measure score of designed pose
		pose.dump_pdb('Designed.pdb')							#Export final pose into a .pdb structure file
		print('---------------------------------------------------------')
		print('Original Structure Score:' , '\t' , score1_original_before_relax)
		print('Relaxed Original Score:' , '\t' , score2_original_after_relax)
		print('Relaxed Design Score:' , '\t\t' , score3_of_design_after_relax)

#11 - Find RMDS Between Two Structures
def RMSD(pose1 , pose2):
	''' To calculate the RMDS between two poses '''
	''' Returns value as integer '''
	RMSD = rosetta.core.scoring.CA_rmsd(pose1 , pose2)
	return(RMSD)

#12 - Fragment Generation and Identification
class Fragment():
	#12.1 - Make The 3-mer and 9-mer Fragment Files
	def Make(pose):
		''' Submits the pose to the Robetta Server (http://www.robetta.org) for fragment generation that are used for the Abinitio folding simulation '''
		''' Generates the 3-mer file, the 9-mer file, and the PsiPred file '''
		sequence = pose.sequence()
		#1 - Post
		web = requests.get('http://www.robetta.org/fragmentsubmit.jsp')
		payload = {
			'UserName':'houcemeddine',
			'Email':'',
			'Notes':'structure',
			'Sequence':sequence,
			'Fasta':'',
			'Code':'',
			'ChemicalShifts':'',
			'NoeConstraints':'',
			'DipolarConstraints':'',
			'type':'submit'
		}
		session = requests.session()
		response = session.post('http://www.robetta.org/fragmentsubmit.jsp', data=payload , files=dict(foo='bar'))
		
		for line in response:
			line = line.decode()
			if re.search('<a href="(fragmentqueue.jsp\?id=[0-9].*)">' , line):
				JobID = re.findall('<a href="(fragmentqueue.jsp\?id=[0-9].*)">' , line)
		JobURL = 'http://www.robetta.org/' + JobID[0]
		#2 - Check
		while True:
			Job = urllib.request.urlopen(JobURL)
			jobdata = bs4.BeautifulSoup(Job , 'lxml')
			status = jobdata.find('td', string='Status: ').find_next().text
			if status == 'Complete':
				print(datetime.datetime.now().strftime('%d %B %Y @ %H:%M') , 'Status:' , status)
				break		
			else:
				print(datetime.datetime.now().strftime('%d %B %Y @ %H:%M') , 'Status:' , status)
				time.sleep(1800)
				continue
		#3 - Download
		sequence = pose.sequence()
		fasta = Resfile = open('structure.fasta' , 'w')
		fasta.write(sequence)
		fasta.close()
		JobID = JobURL.split('=')
		os.system('wget http://www.robetta.org/downloads/fragments/' + str(JobID[1])  + '/aat000_03_05.200_v1_3')
		os.system('wget http://www.robetta.org/downloads/fragments/' + str(JobID[1])  + '/aat000_09_05.200_v1_3')
		os.system('wget http://www.robetta.org/downloads/fragments/' + str(JobID[1])  + '/t000_.psipred_ss2')
	#12.2 - Measure The Number of 9-mer Fragments That Are Below 1Å RMSD
	def Quality(pose):
		''' Measures the quality of the 9-mer fragment files before an Abinitio folding simulation '''
		''' Returns the number of good fragments (below 1Å) as integer '''
		#Choose Fragment
		fragset = ConstantLengthFragSet(9)						#Only use 9-mer because 3-mer is not informative enough
		fragset.read_fragment_file('9-mer')
		#Run Calculator
		calc = FragQualCalculator(fragset , 1.0 , 30.0)
		frags = calc.get('num_goodfrag' , pose)
		return(frags)
	#12.3 - Calculate The Best Fragment's RMSD At Each Position And Plot The Result
	def RMSD(pose , Fragment_File):
		''' Measures the RMSD for each fragment at each position and plots the lowest RMSD fragment for each positon '''
		''' Generates an RMSD vs Position PDF plot '''
		frag = open(Fragment_File , 'r')
		rmsd = open('temp.dat' , 'w')
		for line in frag:
			if line.startswith(' position:'):
				line = line.split()
				size = line[1]
		frag.close()
		count = 0
		for x in range (int(size)):
			count +=1
			#Get the pose and make a copy of it to apply changes to
			pose_copy = Pose()
			pose_copy.assign(pose)
			#Setup frame list
			frames = FrameList()
			#Setup the 9-mer fragment (9-mer is better than 3-mer for this analysis)
			fragset = ConstantLengthFragSet(9)
			fragset.read_fragment_file(Fragment_File)
			fragset.frames(count , frames)
			#Setup the MoveMap
			movemap = MoveMap()
			movemap.set_bb(True)
			#Setup and apply the fragment inserting mover
			for frame in frames:
				for frag_num in range( 1 , frame.nr_frags() + 1 ):
					frame.apply(movemap , frag_num , pose_copy)
					#Measure the RMSD difference between the original pose and the new changed pose (the copy)
					RMSD = rosetta.core.scoring.CA_rmsd(pose , pose_copy)
					print(RMSD , '\t' , count)
					rmsd.write(str(RMSD) + '\t' + str(count) + '\n')
					#Reset the copy pose to original pose
					pose_copy.assign(pose)
		rmsd.close()
		#Analyse the RMSD file to get the lowest RMSD for each position
		data = open('RMSDvsPosition.dat' , 'w')
		lowest = {} 									#Mapping group number -> lowest value found
		for line in open('temp.dat'):
			parts = line.split()
			if len(parts) != 2:							#Only lines with two items on it
				continue
			first = float(parts[0])
			second = int(parts[1])
			if first == 0: 								#Skip line with 0.0 RMSD (this is an error from the 9-mer fragment file). I don't know why it happens
				continue
			if second not in lowest:
				lowest[second] = first
			else:
				if first < lowest[second]:
					lowest[second] = first
		for position, rmsd in lowest.items():
			#print(str(rmsd) + '\t' + str(position))
			data.write(str(position) + '\t' + str(rmsd) + '\n')
		data.close()
		gnuplot = open('gnuplot_sets' , 'w')
		gnuplot.write("""set terminal postscript
set output './plot.pdf'
set encoding iso_8859_1
set term post eps enh color
set xlabel 'Position'
set ylabel 'RMSD (\\305)'
set yrange [0:]
set xrange [0:]
set xtics 1
set xtics rotate 
set title 'Fragment Quality'
set key off
set boxwidth 0.5
set style fill solid
plot 'RMSDvsPosition.dat' with boxes
exit""")
		gnuplot.close()
		os.system('gnuplot < gnuplot_sets')
		os.remove('gnuplot_sets')
		os.remove('temp.dat')

#13 - Denovo Design
def DeNovo2(pose):
	''' Preforms De Novo Design on a protein's structure using the BluePrintBDR Mover. Best to design protein with only helix (no sheets) '''
	''' Generates a BDR.pdb file '''
	scorefxn = get_fa_scorefxn()
	pose.dump_pdb('temp.pdb')
	SS=list()
	p = Bio.PDB.PDBParser()
	structure = p.get_structure('X' , 'temp.pdb')
	model = structure[0]
	dssp = Bio.PDB.DSSP(model , 'temp.pdb')
	for structure in dssp:
		if structure[2] == 'G' or structure[2] == 'H' or structure[2] == 'I':
			rename = 'H'
		elif structure[2] == 'B' or structure[2] == 'E':
			rename = 'E'
		else:
			rename = 'L'
		SS.append(rename)
	start = 0
	end = 9
	loops = pose.total_residue()/5
	for section in range(int(loops)):
		blueprint = open('blueprint' , 'w')
		count = 0
		for secondary_structure in SS:
			if start <= count <= end:
				count += 1
				line = str(count) + ' V ' + str(secondary_structure) + 'X R\n'
				blueprint.write(line)
			else:
				count += 1
				line = str(count) + ' V ' + str(secondary_structure) + 'X .\n'
				blueprint.write(line)
		blueprint.close()
		start += 5
		end += 5
		mover = pyrosetta.rosetta.protocols.fldsgn.BluePrintBDR()
		mover.use_abego_bias(True)
		mover.set_blueprint('blueprint')
		mover.apply(pose)
	pose.dump_pdb('DeNovo.pdb')
	os.remove('temp.pdb')
	os.remove('blueprint')

# - Epigrafting ???
# - Symmetric Design
#--------------------------------------------------------------------------------------------------------------------------------------
#List of All Functions And Their Arguments
'''
Motif(Protein , Chain , Motif_from , Motif_to)
PSIPRED(pose)
print(ProtLayers('structure.pdb'))
print(Decision(score_before , score_after))
Relax(pose)
SASA(pose)
print(Score.ALL(pose))
print(Score.AA(pose))
PyMol.Start()
PyMol.Update(pose)
PyMol.Energy(pose)
Design.Whole(pose)
Design.Layer(pose)
Design.Pack(pose)
Design.Motif(pose , Motif_from , Motif_to)
print(RMSD(pose1 , pose2))
Fragment.Make(pose)
print(Fragment.Quality(pose))
Fragment.RMSD(pose , '9-mer')
Blueprint('structure.pdb')
DeNovo(pose)
'''
#--------------------------------------------------------------------------------------------------------------------------------------
#The Protocol


pose = pose_from_pdb('structure.pdb')

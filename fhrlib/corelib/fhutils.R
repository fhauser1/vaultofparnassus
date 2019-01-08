##### functions adaptations from python only unix linux mac ############

os.path <- function(cdir){
	initial.cwd <- getwd()

	abs.path <- system(paste('cd ',cdir, '; pwd'),intern=TRUE)

	message('nabs',abs.path)
	return(abs.path)
}

setupworksetting <- function(topdir,datadir,outdir){
	initial.cwd <- getwd()
	print(topdir)
	topdir <- os.path(topdir)
	message('current wdir set: ',topdir)
	if (file.exists(file.path(topdir,datadir))==FALSE){

	stop('datadir not existing\n', datadir)
	} else {
   	 datadir <- file.path(topdir,datadir)
   	message('datadir exists\n', datadir)
	}
	
	if (file.exists(file.path(topdir,outdir))==FALSE){
		outdir <- file.path(topdir,outdir)
		 dir.create(outdir)
	} else {
		outdir <- file.path(topdir,outdir)
		
		message('outdir exists\n', outdir)
	}
	
	setwd(outdir)
return(list(datadir=datadir,outdir=outdir))	
}

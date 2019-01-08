




loadlis <- function(allinfo) {
    grp <- list()
    for (i in (1:dim(allinfo)[2])) {
        g <- as.vector(allinfo[, i])
        g <- g[!is.na(g)]
        grp <- append(grp, list(g))
    }
    names(grp) <- c(colnames(allinfo))
    return(grp)
}




fh_vennerable <- function(inputfilename, outputfilename) {
    require(Vennerable)
    require(gplots)
    allinfo <- read.table(file = inputfilename, sep = "\t", 
        header = TRUE, na.strings = "NA", strip.white = TRUE)
    grp <- loadlis(allinfo)
    Vstem <- Venn(grp)
    pdf(file = outputfilename)
    plot(Vstem, doWeights = FALSE)
    dev.off()
    
    graphics.off()
}

fh_venneuler <- function(inputfilename, outputfilename) {
	library(rJava)
    library(venneuler)

    allinfo<-read.table(file=inputfilename,sep='\t',header=TRUE,na.strings = 'NA',strip.white=TRUE,row.names=1)
    v<-venneuler(allinfo)
    
    pdf(file=outputfilename)
    plot(v)
    dev.off()
    graphics.off()
}


fh_venndiag <- function(inputfilename, outputname) {
    require(VennDiagram)
    require(gplots)
    allinfo <- read.table(file = inputfilename, sep = "\t", header = TRUE, na.strings = "NA", strip.white = TRUE)
    grp <- loadlis(allinfo)
    tiff(file = outputname)
    venn.diagram(grp,outputname)
    dev.off()
    graphics.off()
}


fh_evenn <- function(inputdir,nomstr,outputdir) {
    require(eVenn)

    evenn(annot = TRUE, ud = FALSE, prop=FALSE,overlaps=TRUE,pathRes=outputdir,pathLists = c(inputdir), noms=nomstr )
    
}


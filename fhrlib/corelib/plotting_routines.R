#### ggplot routines #####
# library(ggplot2)
# library(grid)
# library(RColorBrewer)
# library(beeswarm)
# library(plyr)
# library(reshape2)
# library(gplots)
# library(histogram)
# library(graphics)
# library(lattice)

dopdfgraph <- function(graphobj,filename,width=7,height=7,gformat='pdf'){
    # helper for pdf 
    graphics.off()
    
    if (gformat=='png'){
        ppi <- 300
        png(filename = paste(unlist(strsplit(filename,"\\."))[1],'.png'),width=6*ppi, height=6*ppi, res=ppi, type = "cairo-png")
        } else {
            
            pdf(file =filename, width, height)
        }
    plot(graphobj)
    message('dopdfgraph done')

    graphics.off()
}

theme_fhbw <- function(base_size = 12) {
  ggplot2::theme(
    axis.line =         ggplot2::element_blank(),
    axis.text.x =       ggplot2::element_text(size = base_size * 0.9 , lineheight = 0.9, vjust = 1),
    axis.text.y =       ggplot2::element_text(size = base_size * 0.9, lineheight = 0.9, hjust = 1),
    axis.ticks =        ggplot2::element_line(colour = "black", size = 0.2),
    axis.title.x =      ggplot2::element_text(size = base_size, vjust = 1),
    axis.title.y =      ggplot2::element_text(size = base_size, angle = 90, vjust = 0.5),
    axis.ticks.length = grid::unit(0.3, "lines"),
    axis.text = ggplot2::element_text(margin=ggplot2::margin(5,5,10,5,"pt")),
 
    legend.background = ggplot2::element_rect(colour=NA), 
    legend.key =        ggplot2::element_rect(colour = NA),
    legend.key.size =   grid::unit(1.2, "lines"),
    legend.text =       ggplot2::element_text(size = base_size * 0.9),
    legend.title =      ggplot2::element_text(size = base_size * 0.9, face = "bold", hjust = 0),
    legend.position =   "right",
 
    panel.background =  ggplot2::element_rect(fill = "white", colour = NA), 
    panel.border =      ggplot2::element_rect(fill = NA, colour="black"), 
    panel.grid.major =  ggplot2::element_line(colour = "white", size = 0.2),
    panel.grid.minor =  ggplot2::element_line(colour = "white", size = 0.2),
    panel.margin =      grid::unit(0.25, "lines"),
 
    strip.background =  ggplot2::element_rect(fill = "white", colour = "grey20"), 
    strip.text.x =      ggplot2::element_text(size = base_size * 0.8),
    strip.text.y =      ggplot2::element_text(size = base_size * 0.8, angle = -90),
 
    plot.background =   ggplot2::element_rect(colour = NA),
    plot.title =        ggplot2::element_text(size = base_size * 1.2),
    plot.margin =       grid::unit(c(1, 1, 0.5, 0.5), "lines")
        )
}


color2fun <- function (group){
	
	# color selection for fill depending on group
    fillis <- list(bw=NULL, grey=ggplot2::scale_fill_grey(),hue=ggplot2::scale_fill_hue(),brew=ggplot2::scale_fill_brewer(palette='Paired'))

	# color selection for point depending on group
	pointlinlis <- list(grey=ggplot2::scale_color_grey(),hue=ggplot2::scale_color_hue(),brew=ggplot2::scale_colour_brewer(palette='Paired'))
    aesfillmode <- list(grey=NA,hue=group,brew=group)
    
    return (list(fill=fillis,poli=pointlinlis,aesfill=aesfillmode))
    }


fhp_ggbase <- function(tabdata,xvar,yvar,group,colormode){


    message(paste('plotparameters:',paste('xvar:',xvar),paste('yvar:',yvar),paste('group:',group),colormode,sep='\n'))
    
    pwf <- ggplot2::ggplot(tabdata)
    
    if (yvar == "") {
        message("NO yvar")
        if (is.na(group)==TRUE) {
            message("group is NA")
            pwf  <- pwf+ ggplot2::aes_string(x = xvar)
            funlis <- color2fun('1')
            
            } else {
                message(paste("ggbase group is ",group))
                
                pwf  <- pwf+ ggplot2::aes_string(x = xvar,group = group)
                funlis <- color2fun(group)
                
             }
             
    } else if (TRUE %in% is.na(group)) {
        message("ggbase group is NA (is.na)")
        pwf  <- pwf+ ggplot2::aes_string(x = xvar, y = yvar)
        funlis <- color2fun('1')
        
    
    } else {
        message('ggbase setting group',group)
        pwf  <- pwf+ ggplot2::aes_string(x = xvar, y = yvar,group=group)
        funlis <- color2fun(group)
        
    }
    
     message("ggbase done")

    return(list(pwf=pwf,funlis=funlis))
}

fhp_adjustscale<-function(pwf,doscale){
    if (is.vector(doscale,'logical')==FALSE){
        yscalemin <- doscale[1]
        yscalemax <- doscale[2]
        steps <- doscale[3]
        pwf <- pwf+ggplot2::coord_cartesian(ylim=c(yscalemin,yscalemax))+scale_y_continuous(limits=c(yscalemin,yscalemax))
        message('**** scaling ****')
    } else {
        message('no scaling')
        
    }
    
    return(pwf)
    
}


fhp_ggtheme <- function(pwf,group, main,cordflip,graphncol,dolabelflip,colormode) {
    base_size=12
    
    pwf <- pwf + theme_fhbw(base_size)
    
    if (colormode %in% c('bw','grey')){
      message('NO COLOR')
        pwf <- pwf + theme_fhbw(base_size)

} 

    
    if (main != "title") {
        pwf <- pwf +  ggplot2::ggtitle(main)
        
    }   
    if (dolabelflip==TRUE){
        message('Labels flipped')
        pwf <- pwf + ggplot2::theme(axis.text.x  = ggplot2::element_text(angle=90, vjust=1 , size=base_size*0.9))
    }

        if (graphncol!=0){
            message('arrange graphs')
            
        pwf <- pwf+ggplot2::facet_wrap(as.formula(paste('~',group,sep='')),ncol=graphncol)
    }
        if (cordflip == TRUE) {
            message('coordinates flipped')
            
            pwf <- pwf + ggplot2::coord_flip()
        }
  

    
    message("fhp_ggtheme done")
    
    return(pwf)
}

fhp_ggerror <- function(pwf, yvar, error) {
    if (is.na(error)==FALSE)
    pwf <- pwf  + ggplot2::geom_errorbar(ggplot2::aes_string(ymin = paste(yvar, 
            "-", error), ymax = paste(yvar, "+", error)), 
            width = 0.2) #, position = position_dodge(0.9)
    message("fhp_ggerror done")
    
    return(pwf)
}

rggscatterplot <- function(tabdata,xvar,yvar,group=NA,error=NA,main='title',colormode='hue',
    cordflip=FALSE,graphncol=0,doscale=FALSE,dolabelflip=FALSE,reducepnt=FALSE,dofit=c(0,0)){

    message('starting rggscatterplot')
    # write.table(tabdata,file='rggscatterplottest.txt',sep='\t')
    # save(tabdata,file='test.rda')
    
    if (reducepnt==TRUE){
    tabdata[,xvar]<- round(tabdata[,xvar]/5)*5
    tabdata[,yvar] <- round(tabdata[,yvar]/5)*5
    }
    retlist <- fhp_ggbase(tabdata,xvar,yvar,group,colormode)

    pwf <- retlist$pwf
    funlis <- retlist$funlis
    
    pwf<-fhp_adjustscale(pwf,doscale)
    
    if ( FALSE %in% is.na(group)) {
        
        if (TRUE %in% is.numeric(tabdata[, group]) ) {
            message("rggscatterplot group is numeric")
            pwf <- pwf + ggplot2::geom_point(mapping=ggplot2::aes_string(colour = funlis$aesfill[[colormode]]), 
                stat = "identity")
        }
        else {
            message('rggscatterplot', group,'  is character')
            pwf <- pwf + ggplot2::geom_point(mapping=ggplot2::aes_string(colour = funlis$aesfill[[colormode]]), 
                stat = "identity") +funlis$poli[colormode]
        }
    }
    else {
        message("rggscatterplot group is  ",NA)
        
        
        pwf <- pwf + ggplot2::geom_point(mapping=ggplot2::aes_string(shape=funlis$aesfill[[colormode]]),stat = "identity") + ggplot2::scale_shape_identity()
        
    }
    
    if (dofit[1]==0 & dofit[2]== 0){
        message('NO fit')
        
    }  else {
        message(paste('rggscatterplot DOING fit',dofit))
        pwf <- pwf +ggplot2::stat_smooth(ggplot2::aes_string(x=xvar,group=dofit[1]),method=dofit[2])
        
    }
    pwf <- fhp_ggerror(pwf, yvar, error)    
    pwf <- fhp_ggtheme(pwf, group, main,cordflip,graphncol,dolabelflip,colormode)
    
    message("rggscatterplot done")
    
    print(pwf)
    return (pwf)
    
    
}


rgglineplot <- function(tabdata,xvar,yvar,group=NA,error=NA,main='title',colormode='grey',
    cordflip=FALSE,graphncol=0,doscale=FALSE,dolabelflip=FALSE,reducepnt=False, dofit=False){


    retlist <- fhp_ggbase(tabdata, xvar, yvar, group,colormode)
    pwf <- retlist$pwf
    funlis <- retlist$funlis
    pwf<-fhp_adjustscale(pwf,doscale)
    
    pwf<- pwf + ggplot2::geom_point(mapping=ggplot2::aes_string(colour = funlis$aesfill[[colormode]]), stat = "identity") + ggplot2::geom_line()

    pwf <- fhp_ggerror(pwf, yvar, error)
    pwf <- fhp_ggtheme(pwf, group, main,cordflip,graphncol,dolabelflip,colormode)
    
        
    return (pwf)
}




rggbarplot <- function(tabdata,xvar,yvar,group=NA,error=NA,main='title',colormode='hue',
    cordflip=FALSE,graphncol= 0,doscale=FALSE,dolabelflip=FALSE){
    message('starting rggbarplot ')

    # write.table(tabdata,file='test.txt',sep='\t')

    # Use dose as a factor rather than numeric
    tabdata<- tabdata[order(tabdata[[yvar]]),]
    if (is.na(group)==FALSE){
        tabdata <-data.frame(tabdata, stringsAsFactors=TRUE)
        # tabdata[,group] <- lapply(tabdata[,group] , factor)
    } 

    retlist <- fhp_ggbase(tabdata,xvar,yvar,group,colormode)
    pwf <- retlist$pwf
    funlis <- retlist$funlis
    
    pwf<-fhp_adjustscale(pwf,doscale)
    
    
    if (is.na(group)==FALSE){
        pwf <- pwf + ggplot2::geom_bar(mapping=ggplot2::aes_string(fill =funlis$aesfill[[colormode]], color=funlis$aesfill[[colormode]]),stat = "identity", position = ggplot2::position_dodge())
        #+funlis$fill[colormode]

        } else {
            
        pwf <- pwf + ggplot2::geom_bar(stat = "identity", position = ggplot2::position_dodge())#+funlis$fill[colormode]

        } 
    
    
    pwf <- fhp_ggerror(pwf, yvar, error)
    pwf <- fhp_ggtheme(pwf=pwf, group=group, main=main,cordflip=cordflip,graphncol=graphncol,dolabelflip=dolabelflip,colormode=colormode)
    message(' rggbarplot done')
    return (pwf)
}




rggboxplot <- function(tabdata,xvar,yvar,group=NA,error=NA,main='title',colormode='hue',
    cordflip=FALSE,graphncol=0,doscale=FALSE,dolabelflip=FALSE){
        
        # write.table(tabdata,file='test.txt',sep='\t')

        # Use dose as a factor rather than numeric

        if (is.na(group)==FALSE){
            tabdata <-data.frame(tabdata, stringsAsFactors=TRUE)
            # tabdata[,group] <- lapply(tabdata[,group] , factor)
        } 
        ymin_set <- min(tabdata[,yvar])-1
        ymax_set <- max(tabdata[,yvar])+1
        # tabdata$intact <- interaction(tabdata[,xvar], tabdata[,yvar])

        retlist <- fhp_ggbase(tabdata,xvar,yvar,group,colormode)
        pwf <- retlist$pwf
        funlis <- retlist$funlis

        pwf <- pwf + ggplot2::geom_boxplot(ggplot2::aes_string(fill=funlis$aesfill[[colormode]], outlier.shape = 1))
        #+funlis$fill[[colormode]]
        pwf<-fhp_adjustscale(pwf,doscale)

        pwf <- fhp_ggtheme(pwf, group, main,cordflip,graphncol,dolabelflip,colormode)

        return (pwf)
    }
    
rggbeeswarm <- function(tabdata,xvar,yvar,group=NA,error=NA,main='title',colormode='hue',
        cordflip=FALSE,graphncol=0,doscale=FALSE,dolabelflip=FALSE){


    message('\n###### beeswarm ###### \n')
    #write.table(tabdata,file='test.txt',sep='\t')
        
    # Use dose as a factor rather than numeric
    if (is.na(group)==FALSE){
        tabdata <-data.frame(tabdata, stringsAsFactors=TRUE)
        # tabdata[,group] <- lapply(tabdata[,group] , factor)
    } 
    ymin_set <- min(tabdata[,yvar])-1
    ymax_set <- max(tabdata[,yvar])+1


    retlist <- fhp_ggbase(tabdata,xvar,yvar,group,colormode)
    pwf <- retlist$pwf
    funlis <- retlist$funlis

    pwf <- pwf + ggplot2::geom_boxplot(ggplot2::aes_string(fill=funlis$aesfill[[colormode]]), outlier.shape = 1)+funlis$fill[colormode]
    pwf<- pwf+ ggplot2::geom_point(ggplot2::aes_string(colour=group ),stat='identity',position = ggplot2::position_dodge()) +funlis$poli[colormode]
    pwf<-fhp_adjustscale(pwf,doscale)

    pwf <- fhp_ggtheme(pwf, group, main,cordflip,graphncol,dolabelflip,colormode)
    
    
    return(pwf)
    
}


rgghistogram <- function(tabdata,xvar,yvar,group=NA,error=NA,main='title',colormode='hue',
    cordflip=FALSE,graphncol=0,doscale=FALSE,dolabelflip=FALSE){
    # write.table(tabdata,file='test.txt',sep='\t')
    message('\n###### rgghistogram ###### \n')

    # Use dose as a factor rather than numeric
    # tabdata[,xvar] <- factor(tabdata[,xvar],as.character(unique(tabdata[,xvar]))) 
    # ymin_set <- min(tabdata[,yvar])-1
    # ymax_set <- max(tabdata[,yvar])+1

    # palete <- getcolormode()
    if (is.na(group)==FALSE){
        tabdata <-data.frame(tabdata, stringsAsFactors=TRUE)
        # tabdata[,group] <- lapply(tabdata[,group] , factor)
    } 
    retlist <- fhp_ggbase(tabdata,xvar,yvar,group,colormode)
    
    
    pwf <- retlist$pwf
    funlis <- retlist$funlis
    
    
    pwf <- pwf + ggplot2::geom_histogram(binwidth=.5, alpha=.5, position="dodge",ggplot2::aes_string(fill=group)) +funlis$fill[colormode]

    # pwf <- fhp_ggerror(pwf, yvar, error)
    pwf<-fhp_adjustscale(pwf,doscale)

    pwf <- fhp_ggtheme(pwf, group, main,cordflip,graphncol,dolabelflip,colormode)


    return (pwf)
}

denshelper <- function(tabdata, group, xvar) {
  res <- plyr::ddply(tabdata, c(group), function(x,ind){ mean(x[,ind]) },xvar)
  return (res)
}

rggdensity <- function(tabdata,xvar,yvar,group=NA,error=NA,main='title',colormode='hue',
    cordflip=FALSE,graphncol=0,doscale=FALSE,dolabelflip=FALSE){
    # write.table(tabdata,file='test.txt',sep='\t')
    message('\n###### rggdensity ###### \n')


    retlist <- fhp_ggbase(tabdata,xvar,yvar,group,colormode)
    pwf <- retlist$pwf
    funlis <- retlist$funlis

    cdf <- denshelper(tabdata, group, xvar)
    V1 <- "V1"
    # print 
    pwf <- pwf + ggplot2::geom_density(alpha=0.2, ggplot2::aes_string(fill=funlis$aesfill[[colormode]])) 
    pwf <- pwf + ggplot2::geom_vline(tabdata=cdf, ggplot2::aes_string(xintercept=V1,  colour=group),
               linetype="dashed", size=1)+scale_fill_hue()
    pwf <- fhp_ggerror(pwf, yvar, error)

    pwf<-fhp_adjustscale(pwf,doscale)

    pwf <- fhp_ggtheme(pwf, group, main,cordflip,graphncol,dolabelflip,colormode)

    return (pwf)
}




rggheatplot <- function(tabdata,xvar,yvar,group=NA,error=NA,main='title',colormode='hue',
    cordflip=FALSE,graphncol= 0,doscale=FALSE,dolabelflip=FALSE){

    message('starting rggheatplot ')
   
    funlis <- color2fun(group)
    # myPalette <- colorRampPalette(rev(brewer.pal(11, "Spectral")),interpolate="linear",bias=2.0)
    myPalette<-colorRampPalette(rev(c("#7F0000", "red", "#FF7F00", "yellow","#7FFF7F", "cyan", "#007FFF", "blue", "#00007F")),space="Lab",interpolate="linear",bias=3.0)
    
    save(yvar,file='yvar.r')
    write.table(tabdata,file='test.txt',sep='\t')
    tabdata <- read.table('test.txt',sep='\t')
    yvar <- as.character(yvar)
    mtrx<-as.matrix(tabdata[,c(yvar)])
    rownames(mtrx)<-tabdata[,xvar]

    longData <- reshape2::melt(mtrx)
    
    
    # Use dose as a factor rather than numeric
    pwf <-  ggplot2::ggplot(longData,aes(x = Var2, y = Var1, fill = value))
    pwf <- pwf + ggplot2::geom_tile()
    pwf <- pwf + ggplot2::scale_fill_gradientn(colours = myPalette(100))
    pwf <- pwf + ggplot2::scale_x_discrete(expand = c(0, 0))
    pwf <- pwf + ggplot2::scale_y_discrete(expand = c(0, 0))
    pwf <- pwf + ggplot2::coord_equal()

    pwf <- fhp_ggtheme(pwf=pwf, group=group, main=main,cordflip=cordflip,graphncol=graphncol,dolabelflip=dolabelflip,colormode=colormode)
    message(' rggheatplot done')
    print(pwf)
    return (pwf)
}
 
rsimpleheatmap<-function(tabdata,scale,dendros,roworder,colorder){
    # direkt heatmap without
    # changing cluster and other methods
    # prevents errors in clusterings
    
    datamatrix<-as.matrix(tabdata)
    myPalette<-colorRampPalette(rev(c("#7F0000", "red", "#FF7F00", "yellow","#7FFF7F", "cyan", "#007FFF", "blue", "#00007F")),space="Lab",interpolate="linear",bias=3.0)
    gplots::heatmap.2(datamatrix, col = myPalette,Rowv = roworder,Colv = colorder, 
            scale = scale, cexRow = 0.5, cexCol = 0.8, density.info = "none", 
            trace = "none", dendrogram = dendros)
}

rgpplot <- function(dfrtabdata=NULL,xvar=NULL,yvar=NULL,group=NA,error=NULL,title='tmp title'){

    formula <- as.formula(paste(yvar, '~', xvar))
    gplots::plotmeans(formula, tabdata=dfrtabdata,bars=TRUE, p=0.95, minsd=0, mean.labels=FALSE,
              ci.label=FALSE, n.label=TRUE, digits=getOption("digits"),
              col="black", barwidth=1, barcol="blue",
              connect=TRUE, legends=names(means),use.t=TRUE,main=title)
    
    
}

### default plotting functions ####

rgpbarplot <- function(tabdata=NULL,xvar=NULL,yvar=NULL,group=NA,error=NULL,main=NULL){
    par(las = 2)
    
    tabdata <-tabdata[!is.na(tabdata[error]),]
    message(tabdata[[error]])
    gplots::barplot2(height=yvar, axis.lty=1,names.arg = as.character(group), ci.u = c(yvar + tabdata[[error]]), ci.l = c(yvar - tabdata[[error]]), plot.ci = TRUE, main = main, cex.names=0.5)


    
}


fh_histogram <- function(tabdata, outputfile, binalgorithm, 
    breaks, xlegend = "", ylegend = "") {
    # library(KernSmooth)
    if (binalgorithm == "bins") {
        message("bins")
        h <- KernSmooth::dpih(tabdata)
        bins <- seq(min(tabdata) - h, max(tabdata) + h, 
            by = h)
        pdf(file = outputfile)
        hist(tabdata, breaks = bins, col = "blue", xlab = xlegend, 
            ylab = ylegend)
        dev.off()
    }
    else if (binalgorithm == "sturges") {
        pdf(file = outputfile)
        message("Sturges")
        hist(tabdata, breaks = "Sturges", col = "blue", 
            xlab = xlegend, ylab = ylegend)
        dev.off()
    }
    else if (binalgorithm == "histo") {
        pdf(file = outputfile)
        histogram::histogram(tabdata)
        dev.off()
    }
    else if (binalgorithm == "default") {
        pdf(file = outputfile)
        hist(tabdata, breaks = breaks, col = "blue", xlab = xlegend, 
            ylab = ylegend)
        dev.off()
    }
    else {
        message("no valid method")
    }
}

fh_barplot <- function(tabdata,grouplabels,outputfile,title='tmp title', xlegend='',ylegend=''){
    
    pdf(file=outputfile)
    par(oma=c(2,2,2,2),las=2 ,mar=c(11,2,2,0.1), cex=0.8,ps=10)
        barplot(tabdata, col='blue', xlab=xlegend,ylab=ylegend,names.arg=grouplabels,plot=TRUE)
        dev.off()
}


matrix.axes <- function(tabdata) {

x <- (1:dim(tabdata)[1]-1)/ (dim(tabdata)[1]-1);
axis(side=1, at=x, labels=rownames(tabdata), las=2);
# Do the columns
x <- (1:dim(tabdata)[2]-1) / (dim(tabdata)[2]-1);
axis(side=2, at=x, labels=colnames(tabdata), las=2);
}


famheat <- function(valmax,infile,outfile,outdir){
    # require(gplots)
    # require(RColorBrewer)
    # require(graphics)
    # require(lattice)
    graphics.off()
    mypalette <-colorRampPalette(c("#00007F", "blue", "#007FFF", "cyan","#7FFF7F", "yellow", "#FF7F00", "red"),interpolate="linear",bias=1.5)
    famrel<-read.table(paste(outdir,infile,sep=''),header=TRUE,sep='\t',row.names=1,na.string='NA')
    famrel <- as.matrix(famrel)
    
    pdf(file=paste(outdir,'heatmap_',outfile,sep=''))
    par(las=2)
    
    hv <- heatmap.2(famrel,scale="none", col=mypalette, trace="none",margins=c(5,15),key=TRUE, Colv=FALSE, dendrogram='none', Rowv=FALSE, keysize=1,cexRow=1.0,cexCol=1.0, na.rm=TRUE)
    dev.off()
    message('heatmap done')
    mypalette <-colorRampPalette(c("#00007F", "blue", "#007FFF", "cyan","#7FFF7F", "yellow", "#FF7F00", "red"),interpolate="linear",bias=1.5)

    pdf(file=paste(outdir,'contour_',outfile,sep=''))
    par(las=2)

    filled.contour(famrel, plot.axes=matrix.axes(as.matrix(famrel)),nlevels=valmax,zlim=c(0,valmax),color.palette=mypalette,main="Familydefinition relation")
    dev.off()
    message('contour done')

    mypalette <-colorRampPalette(c("#00007F", "blue", "#007FFF", "cyan","#7FFF7F", "yellow", "#FF7F00", "red"),interpolate="linear",bias=1.5)
    pdf(file=paste(outdir,'levelplot_',outfile,sep=''))
    par(las=2)
    
    lp<-levelplot(famrel,pretty=TRUE,regions=TRUE, colorkey=TRUE,col.regions=mypalette,main="Familydefinition relation")
    plot(lp)
    dev.off()
    message('levelplot done')
    graphics.off()
    
    
}

rggbeeswarm2 <- function(tabdata,xvar,yvar,group=NA,error=NA,main='title',colormode='hue',
        cordflip=FALSE,graphncol=0,doscale=FALSE,dolabelflip=FALSE){

    message('\n###### beeswarm ###### \n')
    # write.table(tabdata,file='test.txt',sep='\t')

    tabdata = tabdata[ order( tabdata[[xvar]] ) , ]

    if (is.na(group)==TRUE) {
        bform<-as.formula(paste(yvar, '~', xvar))
    } else {
       
        bform<-as.formula(paste(yvar, '~', xvar,'+',group))
        
    }
    beefrm <- beeswarm::beeswarm(bform, tabdata = tabdata, method = 'swarm',pwcol =get(group), do.plot = FALSE)
    colnames(beefrm) <- c(xvar, yvar, "ER", group)


    pwf <- ggplot2::ggplot(beefrm, aes(x, y)) + xlab("") + ggplot2::scale_y_continuous(paste(yvar))
    pwf <- pwf + ggplot2::geom_boxplot(aes(x, y, group = plyr::round_any(x, 1, round)), outlier.shape = 1)
    xlab <- as.list(unique((tabdata[,xvar])))
    pwf <- pwf + ggplot2::geom_point(ggplot2::aes_string(color=group)) + ggplot2::scale_x_continuous(breaks = c(1:length(xlab)), labels = c(xlab), expand = c(0, 0.05))
    pwf <- fhp_ggtheme(pwf, group, main,cordflip,graphncol,dolabelflip,colormode)
    return(pwf)
    
}

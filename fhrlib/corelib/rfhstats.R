## Summarizes data.
## Gives count, mean, standard deviation, standard error of the mean, and confidence interval (default 95%).
##   data: a data frame.
##   measurevar: the name of a column that contains the variable to be summariezed
##   groupvars: a vector containing names of columns that contain grouping variables
##   na.rm: a boolean that indicates whether to ignore NA's
##   conf.interval: the percent range of the confidence interval (default is 95%)

summarySE <- function(data=NULL, measurevar=NULL, groupvars=NULL, na.rm=FALSE, conf.interval=.95) {
    # require(doBy)
    # New version of length which can handle NA's: if na.rm==T, don't count them
    length2 <- function (x, na.rm=FALSE) {
        if (na.rm) sum(!is.na(x))
        else       length(x)
    }

    # Collapse the data
    formula <- as.formula(paste(measurevar, paste(groupvars, collapse=" + "), sep=" ~ "))
    datac <- doBy::summaryBy(formula, data=data, FUN=c(length2,mean,sd,sum,min,max), na.rm=na.rm)
    
    # Rename columns
    names(datac)[ names(datac) == paste(measurevar, ".mean",    sep="") ] <- measurevar
    names(datac)[ names(datac) == paste(measurevar, ".sd",      sep="") ] <- "sd"
    names(datac)[ names(datac) == paste(measurevar, ".length2", sep="") ] <- "N"
    names(datac)[ names(datac) == paste(measurevar, ".sum", sep="") ] <- "sum"
    names(datac)[ names(datac) == paste(measurevar, ".min", sep="") ] <- "min"
    names(datac)[ names(datac) == paste(measurevar, ".max", sep="") ] <- "max"
    
    datac$se <- datac$sd / sqrt(datac$N)  # Calculate standard error of the mean
    
    # Confidence interval multiplier for standard error
    # Calculate t-statistic for confidence interval: 
    # e.g., if conf.interval is .95, use .975 (above/below), and use df=N-1
    ciMult <- qt(conf.interval/2 + .5, datac$N-1)
    datac$ci <- datac$se * ciMult
    
    return(datac)
}


rlongtowide <- function(longdata,measurevar,groupvars){
    dt2<-reshape2::melt(longdata, id = groupvars)
    formulastr <- as.formula(paste(paste(groupvars, collapse=" ~ "),'variable', sep=" + "))
    data.wide <- reshape2::dcast(dt2, formulastr, value.var='value')
    return(data.wide)
}

rwidetolong <- function(origdata.wide,id_vars,measure_vars,variable_name,value_name){
    
    # require(reshape2)
    data.long <- reshape2::melt(origdata.wide,
        # ID variables - all the variables to keep but not split apart on
        id.vars=id_vars,
        # The source columns
        measure.vars=measure_vars,
        # Name of the destination column that will identify the original
        # column that the measurement came from
        variable.name=variable_name,
        value.name=variable.name)
        return(data.wide)
    
}


outlieridentified <- function(dlis,distribution='normal'){
    # require(extremevalues)
    # require(outliers)

    L <- extremevalues::getOutliers(dlis,method="II",alpha=c(0.05, 0.05),distribution=distribution)
    out1= c(L$iRight)
    out2=c(L$iLeft)
    outidx=c()
    dix <- outliers::dixon.test(dlis) #, type = 10, opposite = FALSE, two.sided = TRUE)

    if (dix$p.value<=0.05){
        outidx <- which(dlis == max(dlis))
        dlis <- dlis[-c(outidx)]
        } else {
            
    if (length(L$iRight)!=0){
        outidx <- out1
    }
    
    if (length(L$iLeft)!=0){
        
        outidx <- c(outidx,out2)
    }
    
    if (length(outidx)!=0){
        dlis <- dlis[-c(outidx)]
    }
}
    rv <- list(dlis=dlis,outidx=outidx)
    return (rv)

}

# outlieridentified(c(1,1,2,4,2,5,2,6,3,100))
# outlieridentified(c(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))





stderr <- function(x) sd(x)/sqrt(length(x))
# weightedm
# set.seed(42)   # fix seed so that you get the same results
# dat <- data.frame(assetclass=sample(LETTERS[1:5], 20, replace=TRUE), 
# +                   return=rnorm(20), assets=1e7+1e7*runif(20))
# library(plyr)
# ddply(dat, .(assetclass),   # so by asset class invoke following function
# +       function(x) data.frame(wret=weighted.mean(x$return, x$assets)))
#   assetclass     wret

rdatadescr<-function(numbers){
    
    nmean <- mean(numbers)
    nvar<-var(numbers)
    nsd<-sd(numbers)
    nsem<-stderr(numbers)
    nmedian<-median(numbers)
    nmad<-mad(numbers)
    
    if (length(numbers)>=3){
        nswil<-rshapirowillk(numbers) 
        
        }else{
            nswil<-NA
        }
    return(list(nmean=nmean,nvar=nvar,nsd=nsd,nsem=nsem,nmedian=nmedian,nmad=nmad,nswil=nswil))
}



#Alternative approach using Lund Test
lundcrit<-function(a, n, q) {
# Calculates a Critical value for Outlier Test according to Lund
# See Lund, R. E. 1975, "Tables for An Approximate Test for Outliers in Linear Models", Technometrics, vol. 17, no. 4, pp. 473-476.
# and Prescott, P. 1975, "An Approximate Test for Outliers in Linear Models", Technometrics, vol. 17, no. 1, pp. 129-132.
# a = alpha
# n = Number of data elements
# q = Number of independent Variables (including intercept)
F<-qf(c(1-(a/n)),df1=1,df2=n-q-1,lower.tail=TRUE)
crit<-((n-q)*F/(n-q-1+F))^0.5
crit
}

rgeneralstats <- function(data,group){
    # require(psych)

    if (is.na(group)==FALSE){
        message(paste('group is ',group))
    
    oview <- psych::describeBy(data, data[group])
            
    } else{
        
        oview <- psych::describe(data)
        
    }
    
     psych::pairs.panels(data, pch = ".")

     return(oview=oview)
}

rcorrelation <- function(data,numericvars,method = "spearman", adjust = "holm"){
    message('running corr.test')
    fhdfsub <- data.frame(data[,numericvars])
    fhdfsub <- fhdfsub[complete.cases(fhdfsub),]
    # require(psych)
    corres <- psych::corr.test(fhdfsub, y = NULL, use = "complete", method = method, adjust = adjust)
    return(corres)
    
    
}



rnormcheck <- function(data,numericvars){
    # require(car)
    # require(MASS)
    # require(effects)
    # require(gvlma)

    
    xvar <- numericvars[1]
    yvar <- numericvars[2]
    fhdfsub <- data.frame(data[,numericvars])
    fhdfsub <- fhdfsub[stats::complete.cases(fhdfsub),]
    
    formula <- as.formula(paste(yvar, '~', xvar))
    
    fhdfsublmfit <- stats::lm(formula =formula,data=fhdfsub)
    fhdfsubrlmfit <- MASS::rlm(formula =formula,data=fhdfsub)
    fhdfsubglmfit <- stats::glm(formula =formula,data=fhdfsub)
    
    plot(fhdfsubglmfit)
    

    rsum <- summary(fhdfsublmfit)
    
    car::qqPlot(fhdfsublmfit, main="QQ Plot",simulate=TRUE)
    plot(density(rstudent(fhdfsublmfit)),  main="Density Plot")
    plot(fitted(fhdfsublmfit), rstudent(fhdfsublmfit), col="gray")
    abline(h=0, lty=2)
    lines(lowess(fitted(fhdfsublmfit), rstudent(fhdfsublmfit)))
    #spreadLevelPlot(fhdfsublmfit)
    # crPlots(fhdfsublmfit)
    car::crPlots(fhdfsublmfit,  main="component+residual plot",  ask=FALSE)

    #effects library

    plot(effects::effect(fhdfsublmfit),main="allEffects plot", ask=FALSE)
    
    # glvma library
    
    gvmodel <- gvlma::gvlma(fhdfsublmfit) 
    gvsm <- summary(gvmodel)

    plot(gvmodel)
    # dgvmodel <- deletion.gvlma(gvmodel)
    # dgvsm <- summary(dgvmodel)
    # 
    return(list(gvsm=gvsm,rsum=rsum))
    
}


rshapirowillk<-function(values){

    pvinfo<-stats::shapiro.test(values)
    pv<-pvinfo$p.value
    return(pv)
}

rwelchtest<-function(mean1,sd1,n1,mean2,sd2,n2, alternative, mu, var_equal, conf_level){
    # require(BSDA)
    pv<-BSDA::tsum.test(mean.x=mean1, s.x = sd1, n.x = n1, mean.y = mean2, s.y = sd2,
        n.y = n2, alternative = alternative, mu = 0, var.equal = var_equal,
        conf.level = conf_level)
        return(pv)
}

ranova <- function(data,formulastring,term){
    # perform anova and TukeyHSD 

    formula <- as.formula(formulastring)
    
    aovw <- stats::aov(formula,data = data)
    plot.design(data)
    plot(aovw) 

    aosum <- summary(aovw)   #show the summary table
    print(aosum)
    
    boxplot(formula,data=data)        #graphical summary
    data_hsd <- stats::TukeyHSD(aovw,term)
    plot(data_hsd)
    
    # broom solves the output
    # problem by converting it 
    # into dataframe
    datareform<-broom::tidy(data_hsd)
    aosum<-broom::tidy(aovw)
    
    return(list(aosum=aosum, datareform=datareform))
    
}

rkruskal<-function(data,formulastring,term){
    # require(PMCMR)
    formula <- as.formula(formulastring)
    ktest<-stats::kruskal.test(formula,data=data)
    print(summary(ktest))
    postout<-PMCMR::posthoc.kruskal.nemenyi.test(formula, data = data, dist="Tukey")
    dfdata<-as.data.frame(postout[['p.value']])
    return (dfdata)

    
}


rnonlinfit <- function(data,formulastr,startvalues){
    # dataframe  with columns for values not more
    # formulastr formula for model as string
    # startvalues list with 
    # save(data,file='test.rda')
    require(nlstools)
    require(robustbase)
    require(minpack.lm)
    
    attach(data) # for unknown reasons some functions fail if not attaching
    
    
    fitformula<-as.formula(formulastr)
    
    nlstools::preview(formula=fitformula,data=data,start=startvalues)
    
    # robust non linear fit
    robfitdata<-nlrob(formula=fitformula,data=data,start=startvalues,trace = T)
    
    # nls fit 
    nlfitdata<-nlsLM(formula=fitformula,data=data,start=startvalues,trace = T)
    
    
    resmaf <- nlsResiduals(nlfitdata)
    plot(resmaf)
    
    
    # extraction of yvar and yvar from formula and data
    yvar<-unlist(strsplit(formulastr,split='~'))[1]
    info<-names(data)
    xvar=info[which(info!=yvar)]
    
    
    plot(data[[yvar]]~data[[xvar]])
    s<-seq(min(data[[xvar]]),max(data[[xvar]]),length=length(data[[xvar]]))
    
    lines(s, predict(nlfitdata, list(x = s)), lty = 1, col = "blue")
    lines(s, predict(robfitdata, list(x = s)), lty = 1, col = "magenta")
    legend("topleft", c("nlsLM()", "robust nlrob()"),
           lwd = 1, col= c("blue", "magenta"), inset = 0.05)

    fitparam  <-  as.list(coef(nlfitdata))
    # fitparam  <-  as.list(coef(robfitdata))
    
    detach(data)
    return(fitparam)
    
}

rpcaanalyser <- function(dfrm,variables,qual_sup){
	
	# dfrm : data frame with variables
	# variables : column header of dataframe of columns included in analysis
	# qual_sup: supplemental variables which are factors as vector of columnames
	
	require(FactoMineR)
 	variables <- c(variables,qual_sup)
	dfrm.PCA<-dfrm[, variables]
	hind <- which(variables==qual_sup)
	res<-PCA(dfrm.PCA , scale.unit=TRUE, ncp=5, quali.sup=(hind:hind), graph = FALSE)
	plot.PCA(res, axes=c(1, 2), choix="ind", habillage=hind, col.ind="black", col.ind.sup="blue", col.quali="magenta", label=c("ind", 
	  "ind.sup", "quali"),new.plot=FALSE, title=" locus pca")
	plot.PCA(res, axes=c(1, 2), choix="var", new.plot=FALSE, col.var="black", col.quanti.sup="blue", label=c("var", "quanti.sup"), 
	  lim.cos2.var=0)
	res.hcpc<-HCPC(res ,nb.clust=-1,consol=TRUE,min=3,max=10,graph=F)
	
	plot.HCPC(res.hcpc)
	plot.HCPC(res.hcpc,choice = "tree", draw.tree = TRUE,	new.plot=F)
#	plot.HCPC(res.hcpc,choice = "map", draw.tree = TRUE,label=c("var", "quanti.sup"),	new.plot=F)
	
	# plot.HCPC(res.hcpc,choice = "3D.map",angle=60)


}



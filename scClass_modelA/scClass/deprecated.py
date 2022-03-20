##### scran.py
from rpy2.robjects import r 
import rpy2.robjects as robjects

r('''
    package_install <- function() {
        packages <- c("devtools","BiocManager")
        upgrade_packages <- c("tibble/3.1.4")
        bio_packages <- c("scran","rhdf5")
        git_packages <- c("AllenInstitute/scrattch.io")

        for (p in packages){
            if (!requireNamespace(p, quietly = TRUE)){
                print(paste("Installing package :",p))
                install.packages(p)
            }
            else
                print(paste("Already Install    :",p,">=",packageVersion(p)))
        }
        for (p in upgrade_packages){ 
            p.package <- strsplit(p,"/")[[1]][1]
            p.version <- strsplit(p,"/")[[1]][2]         
            if (!requireNamespace(p.package, quietly = TRUE)){
                print(paste("Installing package :",p.package))
                install.packages(p.package)
            }
            else if(p.version>packageVersion(p.package)){
                print(paste("Installing package :",p.package,">=",p.version))
                install.packages(p.package)
            }
            else
                print(paste("Already Install    :",p.package,">=",packageVersion(p.package)))
        }      
        for (p in bio_packages){
            if (!requireNamespace(p, quietly = TRUE)){
                print(paste("Installing package :",p))
                BiocManager::install(p,update=FALSE,ask=FALSE)
            }
            else
                print(paste("Already Install    :",p,">=",packageVersion(p)))
        }
        for (p in git_packages){
            p.name <-strsplit(p,"/")[[1]][2]
            if (!requireNamespace(p.name, quietly = TRUE)){
                print(paste("Installing package :",p))
                devtools::install_github(p)
            }
            else
                print(paste("Already Install    :",p,">=",packageVersion(p.name)))
        }
    }
    
    get_matrix <- function(path) {
        suppressMessages(library(scran))
        suppressMessages(library(scrattch.io))
        matrix <- read_loom_dgCMatrix(path, chunk_size = 10000, row_names = "ensembl_ids", col_names = "CellID") 
        matrix <- t(matrix)
        return(matrix)
    }
    
    get_cluster <- function(matrix,save=NULL) {
        matrix.cluster <- quickCluster(matrix)
        print("cluster done...")
        if(!is.null(save)){
            write.table(matrix.cluster, file = save, sep = ",")
            print(paste("save cluster result on:",save))
        }
        return(matrix.cluster)
    }
    
    get_size_factor <- function(matrix,matrix.cluster,save=NULL) {
        matrix.sf <- calculateSumFactors(matrix, cluster=matrix.cluster)
        print("size_factor done...")
        if(!is.null(save)){
            write.table(matrix.sf, file = save, sep = ",")
            print(paste("save size_factor result on:",save))
        }
        return(matrix.sf)
    }  
''') 

package_install = robjects.globalenv['package_install']
get_matrix = robjects.globalenv['get_matrix']
get_cluster = robjects.globalenv['get_cluster']
get_size_factor = robjects.globalenv['get_size_factor']

#####  main.py
get a confusion_matrix
def confusion_matrix(y_pred,y_true,_filter=True):
    from sklearn.metrics import confusion_matrix
    import matplotlib.ticker as ticker
    if _filter:
        y_pred = y_pred[y_true>=0]
        y_true = y_true[y_true>=0]
    confmat = confusion_matrix(y_true=y_true, y_pred=y_pred,normalize="true",labels=range(-1,num_out))
    confmat = np.around(confmat*100, decimals=2)
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.matshow(confmat, cmap=plt.cm.Blues, alpha=0.3)
    for i in range(confmat.shape[0]):
        for j in range(confmat.shape[1]):
            ax.text(x=j, y=i, s=confmat[i,j], va='center', ha='center')  
    
    ax.xaxis.set_major_locator(plt.MultipleLocator(1))
    ax.yaxis.set_major_locator(plt.MultipleLocator(1))  
    label = ['(-1)unknown','(0)T-helper cell','(1)cytotoxic T cell','(2)memory B cell','(3)naive B cell','(4)plasma cell',\
             '(5)precursor B cell','(6)pro-B cell','(7)natural killer cell','(8)erythrocyte','(9)megakaryocyte',\
             '(10)monocyte','(11)dendritic cell','(12)BM hematopoietic cell']
    plt.xticks(rotation=90)
    
    ax.xaxis.set_major_locator(ticker.FixedLocator(range(14)))
    ax.yaxis.set_major_locator(ticker.FixedLocator(range(14)))
    ax.set_xticklabels(label)
    ax.set_yticklabels(label)
    plt.xlabel('predicted label(%)')        
    plt.ylabel('true label(%)')
    plt.show() 
    
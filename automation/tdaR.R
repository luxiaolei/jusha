install.packages("TDA")
library("TDA")
version
XX1 <- circleUnif(20)
XX2 <- circleUnif(20, r = 0.2)
DiagLim <- 5
maxdimension <- 1
Diag1 <- ripsDiag(XX1, maxdimension, DiagLim, printProgress = FALSE)
Diag2 <- ripsDiag(XX2, maxdimension, DiagLim, printProgress = FALSE)
bottleneckDist <- bottleneck(Diag1[["diagram"]], Diag2[["diagram"]],
dimension = 1)
print(bottleneckDist)
XX1 <- circleUnif(20)
XX2 <- circleUnif(30, r = 0.2)
DiagLim <- 5
maxdimension <- 1
Diag1 <- ripsDiag(XX1, maxdimension, DiagLim, printProgress = FALSE)
Diag2 <- ripsDiag(XX2, maxdimension, DiagLim, printProgress = FALSE)
bottleneckDist <- bottleneck(Diag1[["diagram"]], Diag2[["diagram"]],
dimension = 1)
print(bottleneckDist)
XX1 <- circleUnif(20)
XX2 <- circleUnif(30, r = 0.2)
DiagLim <- 5
maxdimension <- 1
Diag1 <- ripsDiag(XX1, maxdimension, DiagLim, printProgress = FALSE)
Diag2 <- ripsDiag(XX2, maxdimension, DiagLim, printProgress = FALSE)
bottleneckDist <- bottleneck(Diag1[["diagram"]], Diag2[["diagram"]],
dimension = 0)
print(bottleneckDist)
XX3 <- sphereUnif(20)
?sphereUnif
XX3 <- sphereUnif(20,2)
XX1 <- circleUnif(20)
XX2 <- circleUnif(30, r = 0.2)
DiagLim <- 5
maxdimension <- 1
Diag1 <- ripsDiag(XX1, maxdimension, DiagLim, printProgress = FALSE)
Diag2 <- ripsDiag(XX3, maxdimension, DiagLim, printProgress = FALSE)
bottleneckDist <- bottleneck(Diag1[["diagram"]], Diag2[["diagram"]],
dimension = 0)
print(bottleneckDist)
?torusUnif
XX4 <- torusUnif(300)
XX4 <- torusUnif(300,a=1.8,c=5)
plot(XX4)
XX1 <- circleUnif(20)
XX2 <- circleUnif(30, r = 0.2)
DiagLim <- 5
XX4 <- torusUnif(300)
XX4 <- torusUnif(300,a=1.8,c=5)
plot(XX4)
XX1 <- circleUnif(20)
XX2 <- circleUnif(30, r = 0.2)
DiagLim <- 5
maxdimension <- 1
Diag1 <- ripsDiag(XX1, maxdimension, DiagLim, printProgress = FALSE)
Diag2 <- ripsDiag(XX4, maxdimension, DiagLim, printProgress = FALSE)
bottleneckDist <- bottleneck(Diag1[["diagram"]], Diag2[["diagram"]],
dimension = 0)
print(bottleneckDist)


## confidence set for the Kernel Density Diagram
# input data
n <- 400
XX <- circleUnif(n)
## Ranges of the grid
Xlim <- c(-1.8, 1.8)
Ylim <- c(-1.6, 1.6)
lim <- cbind(Xlim, Ylim)
by <- 0.05
h <- .3 #bandwidth for the function kde
#Kernel Density Diagram of the superlevel sets
Diag <- gridDiag(XX, kde, lim = lim, by = by, sublevel = FALSE,
                 printProgress = TRUE, h = h)
# confidence set
B <- 10 ## the number of bootstrap iterations should be higher!
## this is just an example
alpha <- 0.05
cc <- bootstrapDiagram(XX, kde, lim = lim, by = by, sublevel = FALSE, B = B,
                       alpha = alpha, dimension = 1, printProgress = TRUE, h = h)
plot(Diag[["diagram"]], band = 2 * cc)
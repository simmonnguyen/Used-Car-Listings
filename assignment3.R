setwd("C:/Users/HashT/ITEC4220")

#Loading the dataset
car_data <- read.csv("used_car_listings.csv")

#Preview the dataset
head(car_data)

#1: Plot Mileage vs Price

mileage_thousands <- car_data$mileage / 1000

xticks <- seq(0, max(mileage_thousands, na.rm = TRUE), by = 10)

plot(mileage_thousands, car_data$price,
     main = "Used Car Price vs Mileage",
     xlab = "Mileage (in Miles)",
     ylab = "Price (in USD)",
     pch = 16, col = rgb(0, 0, 1, 0.4),
     cex = 0.7,
     cex.lab = 1.2, cex.axis = 1.1, cex.main = 1.4,
     xaxt = "n")

axis(1, at = xticks, labels = xticks)

#Add a trend line

lines(smooth.spline(mileage_thousands, car_data$price), col = "red", lwd = 2)

legend("topright", legend = c("Car Listings", "Trend Line"),
       col = c("blue", "red"), pch = c(16, NA), lty = c(NA, 1),lwd = c(NA, 2))

#2: Finding the mean and the median of low mileage cars and high mileage cars
low_mileage <- subset(car_data, mileage < 50000)
high_mileage <- subset(car_data, mileage >= 150000)

#Calculating the mean and median of the prices
mean_low <- mean(low_mileage$price, na.rm = TRUE)
mean_high <- mean(high_mileage$price, na.rm = TRUE)

median_low <- median(low_mileage$price, na.rm = TRUE)
median_high <- median(high_mileage$price, na.rm = TRUE)

#Printing Results
mean_low; mean_high
median_low; median_high

#Boxplot to compare visually
boxplot(low_mileage$price, high_mileage$price,
        names = c("Low Mileage (<50k)", "High Mileage (150k+)"),
        main = "Price Comparison: Low vs High Mileage Cars",
        ylab = "Price (USD)",
        col = c("lightblue", "lightgreen"))

#3: Correlation and Regression Analysis
# The Correlation shows a negative correlation because as the mileage increases, 
# price tends to decrease which is what my hypothesis is.

# Remove missing values
car_data <- na.omit(car_data[, c("mileage", "price")])

# Correlation
cor.test(car_data$mileage, car_data$price)

# Simple linear regression: Price ~ Mileage
model <- lm(price ~ mileage, data = car_data)

# Show results
summary(model)

#4
#Histogram of car manufacturing years
car_data$year <- as.numeric(car_data$year)

hist(car_data$year,
     main = "Distribution of Car Manufacturing Years",
     xlab = "Year",
     ylab = "Number of Cars",
     col = "lightblue",
     border = "black",
     breaks = 20)  # control number of bins

# Add a vertical line for the mean year
abline(v = mean(car_data$year, na.rm = TRUE), col = "red", lwd = 2)

# Add text annotation
legend("topleft", legend = "Mean Year", col = "red", lwd = 2)


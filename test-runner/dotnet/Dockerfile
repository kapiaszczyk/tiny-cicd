FROM mcr.microsoft.com/dotnet/sdk:8.0 AS builder

WORKDIR /app

COPY . .

RUN dotnet restore

RUN dotnet build

CMD ["dotnet", "test"]
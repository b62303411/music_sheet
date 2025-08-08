# Use .NET SDK (Alpine) to build the app
FROM mcr.microsoft.com/dotnet/sdk:6.0-alpine AS build
WORKDIR /app

# Install git via Alpine's package manager (no GPG issue)
RUN apk add --no-cache git

# Clone and publish the app
RUN git clone https://github.com/armybuilder/chordieapp.git . \
    && dotnet publish ChordieApp.Web/ChordieApp.Web.csproj -c Release -o /publish

# Use runtime image for final container
FROM mcr.microsoft.com/dotnet/aspnet:6.0-alpine
WORKDIR /app
COPY --from=build /publish .

ENV ASPNETCORE_URLS=http://+:5000
EXPOSE 5000

CMD ["dotnet", "ChordieApp.Web.dll"]

using './main.bicep'

param resourceGroupName = 'vod-demo' // the name of the resource group you created earlier
param resourceLocation = 'swedencentral' // this must be a region where GPT-4 Turbo with Vision is available
param resourceLocationCV = 'swedencentral' // thhis must be a region where Computer Vision with Image Analysis 4.0 is available
param prefix = 'video' // a few alpha characters to make your resources unique
param suffix = 'demo' // a few more alphanumeric characters to make your resources unique
param spObjectId = '9e833457-aa22-4d32-9b99-03f9465bfd64' // the object id of the service principal you created earlier


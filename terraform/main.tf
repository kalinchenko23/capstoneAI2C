provider "azurerm" {
  features {}
  subscription_id = "4da39916-0b38-48bc-acbd-109ba5112537"
}

# Data block to reference the existing resource group but modify this if building from nothing 
data "azurerm_resource_group" "capstone" {
  name = "capstone"
}

# Azure Container Registry (ACR)
resource "azurerm_container_registry" "sofacrcapstone" {
  name                = "sofacrcapstone"
  resource_group_name = data.azurerm_resource_group.capstone.name
  location            = data.azurerm_resource_group.capstone.location
  sku                 = "Basic"
}

# Azure Kubernetes Service (AKS) with SystemAssigned Identity
resource "azurerm_kubernetes_cluster" "capstoneaks" {
  name                = "capstoneaks"
  location            = data.azurerm_resource_group.capstone.location
  resource_group_name = data.azurerm_resource_group.capstone.name
  dns_prefix          = "capstoneaks" # Ensure this is unique

  default_node_pool {
    name       = "default"
    vm_size    = "Standard_A2_v2"
    node_count = 1
  }

  identity {
    type = "SystemAssigned"
  }

    key_vault_secrets_provider {
    secret_rotation_enabled  = true
    secret_rotation_interval = "2h" # Adjust as needed
  }

  tags = {
    environment = "production"
  }
}

# Assign AcrPull role to AKS' system-assigned identity to allow pulling images from ACR
resource "azurerm_role_assignment" "acr_pull" {
  scope                = azurerm_container_registry.sofacrcapstone.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_kubernetes_cluster.capstoneaks.identity[0].principal_id
}

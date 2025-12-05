variable "instance_name" {
  description = "Value of the EC2 instance's Name Tag"
  type        = string
  default     = "WebSocket-Server"
}

variable "instance_type" {
  description = "Value of the EC2 instance's Type"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "Name of the SSH key pair"
  type        = string
}
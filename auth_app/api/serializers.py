from rest_framework import serializers


class RegistrationSerializer(serializers.Serializer):
    """
    Serializer for user registration data.

    Validates that username, email, password, repeated_password, and type are provided,
    and ensures the two password fields match.
    """
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=["customer", "business"])

    def validate(self, data):
        """
        Ensure the provided password and repeated_password match.

        Args:
            data (dict): Incoming validated data containing 'password' and 'repeated_password'.

        Returns:
            dict: The validated data if passwords match.

        Raises:
            serializers.ValidationError: If passwords do not match.
        """
        if data["password"] != data["repeated_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

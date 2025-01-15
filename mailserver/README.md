# Email Sender Project

This project provides functionality to send emails using SMTP, with a focus on sending emails through Gmail. Also includes test cases to ensure the functionality is working as expected.

## Getting Started

To use this package, you'll need to obtain an application-specific password for the Gmail account you want to send emails from. This password is required for authentication when sending emails.

First init the mod:
```bash
go mod init [project name] && go mod tidy
```

Then you can get the two go modules from github:

```bash
go get github.com/jordan-wright/email && go get github.com/stretchr/testify/require
```

### Obtaining Application-Specific Password

To obtain an application-specific password for Gmail:

1. Go to your sender gmail Account settings: [https://myaccount.google.com/](https://myaccount.google.com/)
2. Click on "Security" in the left sidebar.
3. You have to activate the two way factor
4. Go to the two way factor menu and search the application passwords
5. Then you have to create an application and copy the code, that is your password


### Usage

1. Create a `GmailSender` instance using `NewGmailSender` function, providing your name, Gmail address, and the application-specific password.
2. Call the `SendEmail` method of the `GmailSender` instance to send emails.

Here is an example:

```go
package mail

import (
	"testing"
	"github.com/stretchr/testify/require"
)

const EMAIL_SENDER_NAME = "Example Name"
const EMAIL_SENDER_ADRESS = "examplemail@gmail.com"
const EMAIL_SENDER_PASSWORD = "password that google give you"

func TestNewGmailSender(t *testing.T) {

	sender := NewGmailSender(EMAIL_SENDER_NAME, EMAIL_SENDER_ADRESS, EMAIL_SENDER_PASSWORD)

	subject := "Test subject"

	content := `
	<h1>EXAMPLE</h1>
	<p>Hello world!</p>
	`

	to := []string{"exampledestination@gmail.com"}

	attachFiles := []string{"rute to your file to send"}

	err := sender.SendEmail(subject, content, to, nil, nil, attachFiles)

	require.NoError(t, err)

}

```
